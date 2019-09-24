from logging import getLogger
from typing import Any, Callable, Dict, Optional, Tuple, Type

from ...core.request import Body as RequestBody
from ...core.response import Response
from ...core.router import Route
from ...method import MethodType
from ..spec import OpenAPIMethod
from .factories.base import (
    make_core_operation,
    make_json_fields,
    query,
    request,
)
from .factories.headers import request_headers
from .factories.path_args import path_args
from .partial_path import PartialPath


logger = getLogger(__name__)


RequestParams = Dict[Tuple[str, Type[Any]], Type[Any]]


def path(pattern: str, method: MethodType) -> Any:
    def operation_wrapper(
        operation: Callable[..., Response]
    ) -> Callable[..., Response]:
        operation_annotations = {
            k: v
            for k, v in operation.__annotations__.items()
            if k not in ('return', 'body')
        }
        json_fields = make_json_fields(operation_annotations)
        OperationPathArgs = path_args(pattern, operation_annotations)
        headers_names: Dict[str, str] = {}
        OperationRequestHeaders = request_headers(
            operation_annotations, headers_names
        )
        OperationQuery = query(
            OperationPathArgs, headers_names, operation_annotations
        )
        OperationRequestBody = (
            operation.__annotations__.get('body') or Optional[RequestBody]
        )
        OperationRequest = request(
            OperationPathArgs,
            OperationQuery,
            OperationRequestHeaders,
            OperationRequestBody,
        )
        OperationResponse = operation.__annotations__['return']
        core_operation = make_core_operation(
            OperationRequest,
            OperationResponse,
            operation,
            json_fields,
            headers_names,
        )
        route = Route(pattern, method, core_operation)
        partial_path = PartialPath(method=OpenAPIMethod(), route=route)
        core_operation.partial_path = partial_path

        return core_operation

    return operation_wrapper
