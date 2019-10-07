from http import HTTPStatus
from typing import Any, Dict, Sequence

from jsondaora import jsondaora

from .header import Header


@jsondaora
class Response:
    body: Any
    status: HTTPStatus = HTTPStatus.OK
    headers: Sequence[Header] = ()


@jsondaora
class JSONResponse(Response):
    body: Dict[str, Any]
