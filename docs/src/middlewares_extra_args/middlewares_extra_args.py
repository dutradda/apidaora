from typing import Any

from apidaora import (
    MiddlewareRequest,
    Middlewares,
    Response,
    appdaora,
    route,
    text,
)


def request_extra_args(request: MiddlewareRequest) -> None:
    request.kwargs = {'extra': 'You'}


def response_extra_args(
    request: MiddlewareRequest, response: Response
) -> None:
    if request.kwargs and response.kwargs:
        response.body = response.body.replace(
            'You', f"{request.kwargs['extra']} and {response.kwargs['name']}"
        )


@route.get(
    '/middlewares-kwargs',
    middlewares=Middlewares(
        pre_execution=[request_extra_args],
        post_execution=[response_extra_args],
    ),
)
async def extra_args_controller(name: str, **kwargs: Any) -> Response:
    return text(hello(kwargs['extra']), name=name)


def hello(name: str) -> str:
    return f'Hello {name}!'


app = appdaora(extra_args_controller)
