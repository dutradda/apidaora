from typing import Any

from apidaora import Middlewares, Request, Response, appdaora, route, text


def request_extra_args(request: Request) -> None:
    request.ctx['extra'] = 'You'


def response_extra_args(request: Request, response: Response) -> None:
    if request.ctx and response.ctx:
        response.body = response.body.replace(
            'You', f"{request.ctx['extra']} and {response.ctx['name']}"
        )


@route.get(
    '/middlewares-ctx',
    middlewares=Middlewares(
        pre_execution=request_extra_args, post_execution=response_extra_args,
    ),
)
async def extra_args_controller(name: str, **kwargs: Any) -> Response:
    return text(hello(kwargs['extra']), name=name)


def hello(name: str) -> str:
    return f'Hello {name}!'


app = appdaora(extra_args_controller)
