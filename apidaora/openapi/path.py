from dataclasses import dataclass
from logging import getLogger
from typing import (  # type: ignore
    Any,
    Dict,
    Optional,
    Union,
    _GenericAlias,
    _TypedDictMeta,
)

from jsondaora import jsondaora
from jsondaora.schema import JsonField

from ..content import ContentType
from ..core.headers import Headers
from ..core.request import Body as RequestBody
from ..core.request import PathArgs, Query, Request
from ..core.response import Response
from ..core.router import PATH_RE, Route, split_path
from ..exceptions import InvalidPathParams
from ..method import MethodType
from .parameters import Parameter, ParameterType


logger = getLogger(__name__)


def path(pattern: str, method: MethodType) -> Any:
    def wrap(operation: Any) -> Any:
        return_type = operation.__annotations__['return']
        operation_body_type = operation.__annotations__.get('body')
        path_args_matchs = map(lambda p: PATH_RE.match(p), split_path(pattern))
        path_args_names = set(
            match.groupdict()['name'] for match in path_args_matchs if match
        )
        responses = set()
        path_args_type = PathArgs
        query_type = Query
        headers_type = Headers
        request_body_type = Optional[RequestBody]
        path_args_fields = set()
        query_fields = set()
        headers_fields = set()
        optional_fields = set()
        request_params = {}
        headers_names = {}
        json_fields = set()
        operation_bodies = {}

        for param_name, param_type in operation.__annotations__.items():
            if param_name not in ('return', 'body'):
                field = (param_name, param_type)

                if issubclass(param_type, JsonField):
                    json_fields.add(param_name)

                if param_name in path_args_names:
                    path_args_fields.add(field)

                elif (
                    issubclass(param_type, Parameter)
                    and param_type.in_ is ParameterType.HEADER
                ):
                    param_type_name = (
                        param_type.name.replace('-', '_')
                        if param_type.name
                        else None
                    )
                    field_name = param_type_name or param_name

                    if param_type_name:
                        headers_names[param_type_name] = param_name

                    field_type = param_type.schema
                    param_type.annotation_name = param_name

                    if (
                        isinstance(field_type, _GenericAlias)
                        and field_type.__origin__ is Union
                    ):
                        field_types = set()

                        for union_type in field_type.__args__:
                            if (
                                union_type is type(None)  # noqa
                                or union_type is None
                            ):
                                param_type.required = False

                            elif (
                                issubclass(param_type, Parameter)
                                and param_type.in_ is ParameterType.HEADER
                            ):
                                field_types.add(union_type)

                        union_types = [
                            f_type.__name__ for f_type in field_types
                        ]

                        if not param_type.required:
                            union_types.append('None')

                        field_type = Union[eval(', '.join(union_types))]

                    field = (field_name, field_type)

                    if not param_type.required:
                        optional_fields.add(field)

                    headers_fields.add(field)
                    request_params[field] = param_type

                else:
                    query_fields.add(field)

        if len(path_args_fields) != len(path_args_names):
            raise InvalidPathParams()

        if path_args_fields:
            path_args_type = _TypedDictMeta(
                'OperationPathArgs',
                (),
                {'__annotations__': dict(path_args_fields)},
            )
            path_args_type = jsondaora(path_args_type)

        if query_fields:
            query_type = _TypedDictMeta(
                'OperationQuery', (), {'__annotations__': dict(query_fields)}
            )
            query_type = jsondaora(query_type)

        if headers_fields:
            annotations: Dict[str, Any] = {}
            attrs: Dict[str, Any] = {}

            for k, v in headers_fields:
                if (k, v) in optional_fields:
                    v = Optional[v]
                    attrs[k] = None

                annotations[k] = v

            attrs['__annotations__'] = annotations
            headers_type = _TypedDictMeta('OperationHeaders', (), attrs)
            headers_type = jsondaora(headers_type)

        if (
            isinstance(return_type, _GenericAlias)
            and return_type.__origin__ is Union
        ):
            for response_type in return_type.__args__:
                responses.add(response_type)

        if operation_body_type:
            if (
                isinstance(operation_body_type, _GenericAlias)
                and operation_body_type.__origin__ is Union
            ):
                for union_type in operation_body_type.__args__:
                    if not (
                        union_type is type(None) or union_type is None  # noqa
                    ):
                        content_type = union_type.__content_type__

                        if isinstance(content_type, ContentType):
                            operation_bodies[content_type] = union_type

            else:
                content_type = operation_body_type.__content_type__

                if isinstance(content_type, ContentType):
                    operation_bodies[content_type] = operation_body_type

            request_body_type = operation_body_type  # type: ignore

        @dataclass
        class OperationRequest(Request):
            path_args: path_args_type  # type: ignore
            query: query_type  # type: ignore
            headers: headers_type  # type: ignore
            body: request_body_type

        def wrap_operation(req: OperationRequest) -> Response:
            operation_kwargs: Dict[str, Any] = {}
            operation_kwargs.update(req.path_args)
            operation_kwargs.update(req.query)
            operation_kwargs.update(
                (operation_name, req.headers[name])  # type: ignore
                for name, operation_name in headers_names.items()
            )
            operation_kwargs.update(
                (field, operation_kwargs[field].value) for field in json_fields
            )

            if req.body:
                operation_kwargs['body'] = req.body

            response: Response = operation(**operation_kwargs)
            return response

        wrap_operation.__route__ = Route(  # type: ignore
            pattern, method, wrap_operation
        )
        wrap_operation.__responses__ = responses  # type: ignore
        wrap_operation.__request_params__ = request_params  # type: ignore
        wrap_operation.__json_fields__ = json_fields  # type: ignore
        wrap_operation.__headers_names__ = headers_names  # type: ignore
        return wrap_operation

    return wrap
