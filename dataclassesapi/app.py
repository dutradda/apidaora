from http import HTTPStatus
from logging import getLogger
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional
from urllib import parse

import orjson
from dataclassesjson.exceptions import DeserializationError

from dataclassesapi.exceptions import MethodNotFoundError, PathNotFoundError
from dataclassesapi.request import as_request
from dataclassesapi.response import AsgiResponse, Response
from dataclassesapi.response import as_asgi as as_asgi_response
from dataclassesapi.router import Route, Router


logger = getLogger(__name__)


class App:
    _routes: Iterable[Route]

    def __init__(self, routes: Optional[Iterable[Route]] = None):
        self._router = Router()

        if routes is not None:
            self._routes = routes

        self._router.add_routes(self._routes)

    async def __call__(
        self,
        scope: Dict[str, Any],
        receive: Callable[[], Awaitable[Dict[str, Any]]],
        send: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> None:
        headers = scope['headers']

        try:
            resolved = self._router.route(scope['path'], scope['method'])

        except PathNotFoundError:
            await self._send_asgi_response(
                send, AsgiResponse(HTTPStatus.NOT_FOUND)
            )

        except MethodNotFoundError:
            await self._send_asgi_response(
                send, AsgiResponse(HTTPStatus.METHOD_NOT_ALLOWED)
            )

        else:
            query_dict = self._get_query_dict(scope)
            body = await self._read_body(receive)
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
                asgi_response = AsgiResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    body=orjson.dumps(error.dict),
                    headers=headers,
                )
                await self._send_asgi_response(send, asgi_response)

            else:
                response = resolved.route.caller(request)  # type: ignore
                await self._send_response(send, response)

    def _get_query_dict(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        qs = parse.parse_qs(scope['query_string'].decode())
        return qs

    async def _read_body(
        self, receive: Callable[[], Awaitable[Dict[str, Any]]]
    ) -> Any:
        body = b''
        more_body = True

        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        return body

    async def _send_response(
        self,
        send: Callable[[Dict[str, Any]], Awaitable[None]],
        response: Response,
    ) -> None:
        asgi_response = as_asgi_response(response)
        await self._send_asgi_response(send, asgi_response)

    async def _send_asgi_response(
        self,
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
