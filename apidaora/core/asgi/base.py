from typing import Any, Awaitable, Callable, Coroutine, Dict


Scope = Dict[str, Any]
Receiver = Callable[[], Awaitable[Dict[str, Any]]]
Sender = Callable[[Dict[str, Any]], Awaitable[None]]
AsgiCallable = Callable[[Scope, Receiver, Sender], Coroutine[Any, Any, None]]
