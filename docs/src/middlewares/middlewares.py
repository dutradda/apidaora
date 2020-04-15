from jsondaora import jsondaora

from apidaora import (
    CorsMiddleware,
    Header,
    Middlewares,
    Request,
    Response,
    appdaora,
    route,
    text,
)


def pre_execution_middleware(request: Request) -> None:
    if request.body:
        request.body.name = request.body.name.replace('Me', 'You')


def post_execution_middleware(request: Request, response: Response) -> None:
    response.headers = [
        PostExecutionHeader(
            len(response.body.replace('Hello ', '').replace('!', ''))
        )
    ]


# The route middlewares takes precedence over general middlewares


@jsondaora
class PreExecutionBody:
    name: str


@route.post(
    '/hello-pre-execution/',
    middlewares=Middlewares(pre_execution=[pre_execution_middleware]),
)
async def pre_execution_middleware_controller(body: PreExecutionBody) -> str:
    return hello(body.name)


class PostExecutionHeader(Header, type=int, http_name='x-name-len'):
    ...


@route.get(
    '/hello-post-execution',
    middlewares=Middlewares(post_execution=[post_execution_middleware]),
)
async def post_execution_middleware_controller(name: str) -> Response:
    return text(body=hello(name))


def hello(name: str) -> str:
    return f'Hello {name}!'


app = appdaora(
    [
        pre_execution_middleware_controller,
        post_execution_middleware_controller,
    ],
    middlewares=Middlewares(
        post_execution=[CorsMiddleware(servers_all='my-server.domain')]
    ),
)
