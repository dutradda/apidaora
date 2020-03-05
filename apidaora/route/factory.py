import functools
import itertools
from asyncio import iscoroutine
from dataclasses import is_dataclass
from http import HTTPStatus
from json import JSONDecodeError
from typing import (  # type: ignore
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Type,
    Union,
    _GenericAlias,
)

import orjson
from jsondaora import as_typed_dict, dataclass_asjson, typed_dict_asjson
from jsondaora.deserializers import deserialize_field
from jsondaora.exceptions import DeserializationError

from ..asgi.base import (
    ASGIBody,
    ASGICallableResults,
    ASGIHeaders,
    ASGIPathArgs,
    ASGIQueryDict,
    ASGIResponse,
)
from ..asgi.responses import (
    NOT_FOUND_RESPONSE,
    NO_CONTENT_RESPONSE,
    make_html_response,
    make_json_response,
    make_text_response,
)
from ..asgi.router import Controller, Route
from ..bodies import GZipFactory
from ..content import ContentType
from ..exceptions import BadRequestError, InvalidReturnError
from ..header import Header
from ..method import MethodType
from ..responses import Response
from .controller_input import controller_input


RESPONSES_MAP: Dict[
    Union[ContentType, HTTPStatus],
    Union[Callable[..., ASGIResponse], ASGIResponse,],
] = {
    ContentType.APPLICATION_JSON: make_json_response,
    ContentType.TEXT_PLAIN: make_text_response,
    ContentType.TEXT_HTML: make_html_response,
    HTTPStatus.NOT_FOUND: NOT_FOUND_RESPONSE,
    HTTPStatus.NO_CONTENT: NO_CONTENT_RESPONSE,
}


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
                        name: deserialize_query_args(
                            name, type_, query_dict.get(name)
                        )
                        for name, type_ in annotations_query_dict.items()
                    }
                )

            if annotations_info.has_headers:
                headers_map = ControllerInput.__headers_name_map__
                kwargs.update(
                    {
                        name: annotations_headers[name](h_value.decode())  # type: ignore
                        for h_name, h_value in headers
                        if (name := headers_map.get(h_name.decode()))  # noqa
                        in annotations_headers
                    }
                )

            if annotations_info.has_body:
                if isinstance(body_type, type) and issubclass(
                    body_type, GZipFactory
                ):
                    kwargs['body'] = body_type(value=body)
                    input_ = as_typed_dict(kwargs, ControllerInput)
                    return input_  # type: ignore
                else:
                    kwargs['body'] = make_json_request_body(body, body_type)

            return as_typed_dict(  # type: ignore
                kwargs, ControllerInput
            )

        return {}

    async def build_asgi_output(
        controller_output: Any,
        status: HTTPStatus = HTTPStatus.OK,
        headers: Optional[Sequence[Header]] = None,
        content_type: Optional[ContentType] = ContentType.APPLICATION_JSON,
        return_type_: Any = None,
    ) -> ASGICallableResults:
        while iscoroutine(controller_output):
            controller_output = await controller_output

        if return_type_ is None and return_type:
            return_type_ = return_type

        if isinstance(controller_output, Response):
            return build_asgi_output(
                controller_output['body'],
                controller_output['status'],
                controller_output['headers'],
                controller_output['content_type'],
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
            isinstance(controller_output, tuple)
            or isinstance(controller_output, str)
            or isinstance(controller_output, list)
            or isinstance(controller_output, int)
            or isinstance(controller_output, bool)
            or isinstance(controller_output, float)
        ):
            if content_type == ContentType.APPLICATION_JSON:
                body = orjson.dumps(controller_output)
            else:
                body = str(controller_output).encode()

        elif controller_output is None:
            content_length = 0 if has_content_length else None

            if content_type is None and status in RESPONSES_MAP:
                return (RESPONSES_MAP[status],)

            if headers:
                return RESPONSES_MAP[content_type](  # type: ignore
                    content_length, headers=make_asgi_headers(headers)
                )

            return RESPONSES_MAP[content_type](content_length)  # type: ignore

        else:
            raise InvalidReturnError(controller_output, controller)

        content_length = len(body) if has_content_length else None

        return (
            RESPONSES_MAP[content_type](  # type: ignore
                content_length, status, make_asgi_headers(headers)
            ),
            body,
        )

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
                    error.dict, has_content_length, error.headers
                )

            except DeserializationError as error:
                error_dict = {
                    'name': 'field-parsing',
                    'message': error.args[0],
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


def make_json_request_body(body: bytes, body_type: Optional[Type[Any]]) -> Any:
    try:
        return orjson.loads(body)
    except JSONDecodeError:
        schema = (
            getattr(body_type, '__annotations__', {}) if body_type else None
        )
        schema = {k: t.__name__ for k, t in schema.items()}
        raise BadRequestError(name='invalid-body', info={'schema': schema})


def send_bad_request_response(
    error_dict: Dict[str, Any],
    has_content_length: bool,
    headers: Optional[Sequence[Header]] = None,
    content_type: ContentType = ContentType.APPLICATION_JSON,
) -> ASGICallableResults:
    body = orjson.dumps({'error': error_dict})
    content_length = len(body) if has_content_length else None

    return (
        RESPONSES_MAP[content_type](  # type: ignore
            content_length, HTTPStatus.BAD_REQUEST, make_asgi_headers(headers)
        ),
        body,
    )


def make_asgi_headers(
    headers: Optional[Sequence[Header]],
) -> Optional[ASGIHeaders]:
    if not headers:
        return None

    return tuple(
        (
            header.http_name.encode(),  # type: ignore
            str(header.value).encode()
            if not isinstance(header.value, bytes)
            else header.value,
        )
        for header in headers
    )


def deserialize_query_args(
    name: str, type_: Type[Any], value: Optional[List[str]]
) -> Any:
    if value is not None:
        if isinstance(type_, _GenericAlias) and type_._name in (
            'List',
            'Tuple',
            'Set',
            'Deque',
        ):
            value = list(itertools.chain(*[v.split(',') for v in value]))

        elif len(value) > 1:
            raise BadRequestError(
                name='invalid-query',
                info={'name': name, 'type': type_, 'value': value},
            )
        else:
            value = value[0]

        return deserialize_field(name, type_, value)
