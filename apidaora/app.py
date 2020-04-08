from typing import Optional, Sequence, Union

from .asgi.app import asgi_app
from .asgi.base import ASGIApp
from .asgi.router import Controller, make_router
from .controllers.background_task import BackgroundTask
from .middlewares import Middlewares


Controllers = Union[
    Controller,
    BackgroundTask,
    Sequence[Union[Controller, BackgroundTask]],
    Sequence[Controller],
    Sequence[BackgroundTask],
]


def appdaora(
    controllers: Controllers, middlewares: Optional[Middlewares] = None
) -> ASGIApp:
    routes = []

    if not isinstance(controllers, Sequence):
        controllers = [controllers]

    for controller in controllers:
        if isinstance(controller, BackgroundTask):
            routes.extend(controller.create.routes)
            routes.extend(controller.get_results.routes)

        else:
            routes.extend(controller.routes)

    return asgi_app(make_router(routes, middlewares=middlewares))
