from http import HTTPStatus
from typing import Any, Dict, Sequence

from jsondaora import jsondaora

from .header import _Header


@jsondaora
class Response:
    body: Any
    status: HTTPStatus = HTTPStatus.OK
    headers: Sequence[_Header] = ()


@jsondaora
class JSONResponse(Response):
    body: Dict[str, Any]
