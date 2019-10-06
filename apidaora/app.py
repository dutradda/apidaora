from typing import Sequence, Union

from .asgi.app import asgi_app
from .asgi.base import ASGIApp
from .asgi.router import make_router
from .route.controller import Controller


def appdaora(handlers: Union[Controller, Sequence[Controller]]) -> ASGIApp:
    routes = []

    if not isinstance(handlers, Sequence):
        handlers = [handlers]

    for operation in handlers:
        routes.append(operation.route)

    return asgi_app(make_router(routes))
