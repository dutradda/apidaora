import functools
from asyncio import iscoroutine
from dataclasses import is_dataclass
from http import HTTPStatus
from json import JSONDecodeError
from typing import Any, Awaitable, Callable, Dict, Union

import orjson
from jsondaora import as_typed_dict, dataclass_asjson, typed_dict_asjson
from jsondaora.exceptions import DeserializationError

from ..asgi.base import (
    ASGIBody,
    ASGICallableResults,
    ASGIHeaders,
    ASGIPathArgs,
    ASGIQueryDict,
)
from ..asgi.responses import make_json_response
from ..asgi.router import Route
from ..exceptions import BadRequestError, InvalidReturnError
from ..method import MethodType
from ..responses import Response
from .controller import Controller
from .controller_input import controller_input


def make_route(
    path_pattern: str,
    method: MethodType,
    controller: Callable[..., Any],
    has_content_length: bool = True,
) -> Route:
    ControllerInput = controller_input(controller, path_pattern)
    annotations_info = ControllerInput.__annotations_info__
    annotations_path_args = ControllerInput.__annotations_path_args__
    annotations_query_dict = ControllerInput.__annotations_query_dict__
    annotations_headers = ControllerInput.__annotations_headers__
    body_type = ControllerInput.__annotations_body__.get('body')
    return_type = controller.__annotations__.get('return')

    def parse_asgi_input(
        path_args: ASGIPathArgs,
        query_dict: ASGIQueryDict,
        headers: ASGIHeaders,
        body: ASGIBody,
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any]
        if annotations_info.has_input:
            if annotations_info.has_path_args:
                kwargs = {
                    name: path_args.get(name)
                    for name in annotations_path_args.keys()
                }
            else:
                kwargs = {}

            if annotations_info.has_query_dict:
                kwargs.update(
                    {
                        name: value
                        if (
                            (value := query_dict.get(name))  # noqa
                            and len(value) > 1  # type: ignore
                        )
                        else value[0]
                        if isinstance(value, list)
                        else None
                        for name in annotations_query_dict.keys()
                    }
                )

            if annotations_info.has_headers:
                headers_map = ControllerInput.__headers_name_map__
                kwargs.update(
                    {
                        name: h_value.decode()  # type: ignore
                        for h_name, h_value in headers
                        if (name := headers_map.get(h_name.decode()))  # noqa
                        in annotations_headers
                    }
                )

            if annotations_info.has_body:
                try:
                    kwargs['body'] = orjson.loads(body)
                except JSONDecodeError:
                    schema = (
                        getattr(body_type, '__annotations__', {})
                        if body_type
                        else None
                    )
                    schema = {k: t.__name__ for k, t in schema.items()}
                    raise BadRequestError(
                        name='invalid-body', info={'schema': schema}
                    )

            return as_typed_dict(kwargs, ControllerInput)  # type: ignore

        return {}

    async def build_asgi_output(
        controller_output: Any,
        status: HTTPStatus = HTTPStatus.OK,
        return_type_: Any = None,
    ) -> ASGICallableResults:
        while iscoroutine(controller_output):
            controller_output = await controller_output

        if return_type_ is None and return_type:
            return_type_ = return_type

        if isinstance(return_type_, type) and issubclass(
            return_type_, Response
        ):
            return build_asgi_output(
                controller_output.body,
                controller_output.status,
                controller_output.__annotations__.get('body'),
            )

        elif isinstance(controller_output, dict):
            if return_type_:
                body = typed_dict_asjson(controller_output, return_type_)
            else:
                body = orjson.dumps(controller_output)

        elif is_dataclass(controller_output):
            body = dataclass_asjson(controller_output)

        elif (
            isinstance(controller_output, str)
            or isinstance(controller_output, int)
            or isinstance(controller_output, bool)
            or isinstance(controller_output, float)
        ):
            body = orjson.dumps(controller_output)

        elif controller_output is None:
            content_length = 0 if has_content_length else None
            return make_json_response(content_length)

        else:
            raise InvalidReturnError(controller_output, controller)

        content_length = len(body) if has_content_length else None
        return make_json_response(content_length, status), body

    class WrappedController(Controller):
        @functools.wraps(controller)
        def __call__(
            self,
            path_args: ASGIPathArgs,
            query_dict: ASGIQueryDict,
            headers: ASGIHeaders,
            body: ASGIBody,
        ) -> Union[Awaitable[ASGICallableResults], ASGICallableResults]:
            try:
                kwargs = parse_asgi_input(path_args, query_dict, headers, body)
                controller_output = controller(**kwargs)
                return build_asgi_output(controller_output)

            except BadRequestError as error:
                return send_bad_request_response(
                    error.dict, has_content_length
                )

            except DeserializationError as error:
                field = {
                    'name': error.args[0].name,
                    'type': error.args[0].type.__name__,
                    'invalid_value': error.args[1],
                }
                error_dict = {
                    'name': 'field-parsing',
                    'info': {'field': field},
                }
                return send_bad_request_response(
                    error_dict, has_content_length
                )

    wrapped_controller = WrappedController()
    route = Route(
        path_pattern,
        method,
        wrapped_controller,
        annotations_info.has_path_args,
        annotations_info.has_query_dict,
        annotations_info.has_headers,
        annotations_info.has_body,
    )
    wrapped_controller.route = route
    return route


def send_bad_request_response(
    error_dict: Dict[str, Any], has_content_length: bool
) -> ASGICallableResults:
    body = orjson.dumps({'error': error_dict})
    content_length = len(body) if has_content_length else None
    return (make_json_response(content_length, HTTPStatus.BAD_REQUEST), body)
