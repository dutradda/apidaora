from typing import Sequence, Union

from .asgi.app import asgi_app
from .asgi.base import ASGIApp
from .asgi.router import Controller, make_router
from .controllers.background_task import BackgroundTask


Controllers = Union[
    Controller,
    BackgroundTask,
    Sequence[Union[Controller, BackgroundTask]],
    Sequence[Controller],
    Sequence[BackgroundTask],
]


def appdaora(controllers: Controllers) -> ASGIApp:
    routes = []

    if not isinstance(controllers, Sequence):
        controllers = [controllers]

    for controller in controllers:
        if isinstance(controller, BackgroundTask):
            routes.append(controller.create.route)
            routes.append(controller.get_results.route)

        else:
            routes.append(controller.route)

    return asgi_app(make_router(routes))
