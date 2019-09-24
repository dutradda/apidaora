from dataclasses import dataclass
from logging import getLogger
from typing import (  # type: ignore
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Set,
    Type,
    _TypedDictMeta,
)

from jsondaora import jsondaora
from jsondaora.schema import JsonField

from ....core.headers import Headers
from ....core.request import Body as RequestBody
from ....core.request import PathArgs, Query, Request
from ....core.response import Response
from ..partial_path import PartialPath


logger = getLogger(__name__)


def make_json_fields(operation_annotations: Dict[str, Any]) -> Set[str]:
    json_fields = set()

    for param_name, param_type in operation_annotations.items():
        if isinstance(param_type, type) and issubclass(param_type, JsonField):
            json_fields.add(param_name)

    return json_fields


def query(
    path_args_type: Type[PathArgs],
    headers_names: Dict[str, str],
    operation_annotations: Dict[str, Any],
) -> Type[Query]:
    query_annotations = {
        k: v
        for k, v in operation_annotations.items()
        if k not in path_args_type.__annotations__
        and k not in headers_names.keys()
        and k not in headers_names.values()
    }

    query_type = _TypedDictMeta(
        'OperationQuery', (Query,), {'__annotations__': query_annotations}
    )
    query_type: Type[Query] = jsondaora(query_type)
    return query_type


def request(
    path_args_type: PathArgs,
    query_type: Query,
    headers_type: Headers,
    body_type: RequestBody,
) -> Type[Request]:
    @dataclass
    class OperationRequest(Request):
        path_args: path_args_type  # type: ignore
        query: query_type  # type: ignore
        headers: headers_type  # type: ignore
        body: body_type

    return OperationRequest


def make_core_operation(
    request_type: Request,
    request_response: Response,
    operation: Callable[..., Response],
    json_fields: Iterable[JsonField],
    headers_names: Dict[str, str],
    partial_path: Optional[PartialPath] = None,
) -> Type[Any]:
    def core_operation(req: request_type) -> request_response:
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

        return operation(**operation_kwargs)

    return core_operation
