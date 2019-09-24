from logging import getLogger
from typing import Any, Callable, Dict, Iterable, Optional, Type

from jsondaora.schema import JsonField

from ....core.request import Request
from ....core.response import Response
from ..partial_path import PartialPath


logger = getLogger(__name__)


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
