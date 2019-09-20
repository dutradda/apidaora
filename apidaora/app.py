from http import HTTPStatus
from logging import getLogger
from typing import Any, Awaitable, Callable, Coroutine, Dict, Iterable
from urllib import parse

import orjson
from jsondaora.exceptions import DeserializationError

from apidaora.exceptions import MethodNotFoundError, PathNotFoundError
from apidaora.request import as_request
from apidaora.response import AsgiResponse, Response
from apidaora.response import as_asgi as as_asgi_response
from apidaora.router import Route, route
from apidaora.router import router as http_router


logger = getLogger(__name__)


Scope = Dict[str, Any]
Receiver = Callable[[], Awaitable[Dict[str, Any]]]
Sender = Callable[[Dict[str, Any]], Awaitable[None]]
AsgiCallable = Callable[[Scope, Receiver, Sender], Coroutine[Any, Any, None]]


def asgi_app(routes: Iterable[Route]) -> AsgiCallable:
    router = http_router(routes)

    async def handler(scope: Scope, receive: Receiver, send: Sender) -> None:
        headers = scope['headers']

        try:
            logger.error(router, scope['path'], scope['method'])
            resolved = route(router, scope['path'], scope['method'])

        except PathNotFoundError:
            await _send_asgi_response(
                send, AsgiResponse(HTTPStatus.NOT_FOUND)  # type: ignore
            )

        except MethodNotFoundError:
            await _send_asgi_response(
                send,
                AsgiResponse(HTTPStatus.METHOD_NOT_ALLOWED),  # type: ignore
            )

        else:
            query_dict = _get_query_dict(scope)
            body = await _read_body(receive)
            request_cls = resolved.route.caller.__annotations__[  # type: ignore
                'req'
            ]

            try:
                request = as_request(
                    request_cls=request_cls,
                    path_args=resolved.path_args,
                    query_dict=query_dict,
                    headers=headers,
                    body=body,
                )

            except DeserializationError as error:
                logger.warning(f"DeserializationError {error.message}")
                asgi_response = AsgiResponse(  # type: ignore
                    status_code=HTTPStatus.BAD_REQUEST,
                    body=orjson.dumps(error.dict),
                    headers=headers,
                )
                await _send_asgi_response(send, asgi_response)

            else:
                response = resolved.route.caller(request)  # type: ignore
                await _send_response(send, response)

    return handler


def _get_query_dict(scope: Dict[str, Any]) -> Dict[str, Any]:
    qs = parse.parse_qs(scope['query_string'].decode())
    return qs


async def _read_body(receive: Callable[[], Awaitable[Dict[str, Any]]]) -> Any:
    body = b''
    more_body = True

    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    return body


async def _send_response(
    send: Callable[[Dict[str, Any]], Awaitable[None]], response: Response
) -> None:
    asgi_response = as_asgi_response(response)
    await _send_asgi_response(send, asgi_response)


async def _send_asgi_response(
    send: Callable[[Dict[str, Any]], Awaitable[None]],
    asgi_response: AsgiResponse,
) -> None:
    await send(
        {
            'type': 'http.response.start',
            'status': asgi_response.status_code.value,
            'headers': asgi_response.headers,
        }
    )
    await send({'type': 'http.response.body', 'body': asgi_response.body})
