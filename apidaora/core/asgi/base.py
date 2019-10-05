from typing import Any, Awaitable, Callable, Coroutine, Dict


Scope = Dict[str, Any]
Receiver = Callable[[], Awaitable[Dict[str, Any]]]
Sender = Callable[[Dict[str, Any]], Awaitable[None]]
ASGICallable = Callable[[Scope, Receiver, Sender], Coroutine[Any, Any, None]]
ASGIPathArgs = Dict[str, str]
ASGIQueryDict = Dict[str, List[str]]
ASGIHeaders = List[Tuple[bytes, bytes]]
ASGIBody = bytes


class ASGIResponse(TypedDict):
    headers: ASGIHeaders
    type: str
    status: int


ASGICallableResults = Union[ASGIResponse, Tuple[ASGIResponse, ASGIBody]]
ASGICallable = Callable[
    [ASGIPathArgs, ASGIQueryDict, ASGIHeaders, ASGIBody], ASGICallableResults
]
