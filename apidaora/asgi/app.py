import asyncio
from http import HTTPStatus
from logging import getLogger
from typing import Any, Awaitable, Callable, Dict
from urllib import parse

import orjson

from ..exceptions import (
    BadRequestError,
    MethodNotFoundError,
    PathNotFoundError,
)
from .base import ASGIApp, Receiver, Scope, Sender
from .responses import (
    make_json_response,
    send_method_not_allowed_response,
    send_not_found,
    send_response,
)
from .router import ResolvedRoute


logger = getLogger(__name__)


def asgi_app(router: Callable[[str, str], ResolvedRoute]) -> ASGIApp:
    async def controller(
        scope: Scope, receive: Receiver, send: Sender
    ) -> None:
        try:
            resolved = router(scope['path'], scope['method'])

        except PathNotFoundError:
            await send_not_found(send)

        except MethodNotFoundError:
            await send_method_not_allowed_response(send)

        else:
            route = resolved.route

            if route.has_headers:
                headers = scope['headers']
            else:
                headers = []

            try:
                if (
                    hasattr(route.controller, 'middlewares')
                    and route.controller.middlewares
                ):
                    for (
                        middleware
                    ) in route.controller.middlewares.post_routing:
                        middleware(route.path_pattern, resolved.path_args)

            except BadRequestError as error:
                body = orjson.dumps(error.dict)
                await send_response(
                    send,
                    response=make_json_response(
                        content_length=len(body),
                        status=HTTPStatus.BAD_REQUEST,
                        headers=headers,
                    ),
                    body=body,
                )
                return

            if route.has_query:
                query_dict = _get_query_dict(scope)
            else:
                query_dict = {}

            if route.has_body:
                body = await _read_body(receive)
            else:
                body = b''

            response_and_body = route.controller(
                resolved.path_args, query_dict, headers, body
            )

            while asyncio.iscoroutine(response_and_body):
                response_and_body = await response_and_body

            response, body = (
                (response_and_body[0], response_and_body[1])
                if len(response_and_body) > 1
                else (response_and_body[0], b'')
            )
            await send_response(send, response, body)

    return controller


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
