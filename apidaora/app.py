from collections import defaultdict
from logging import Logger, getLogger
from typing import Any, DefaultDict, List, Optional, Sequence, Type, Union

from .asgi.app import asgi_app
from .asgi.base import ASGIApp
from .asgi.router import Controller, Route, make_router
from .class_controller import ClassController
from .controllers.background_task import BackgroundTask
from .method import MethodType
from .middlewares import Middlewares
from .options import make_options_controller
from .route.factory import make_route


Controllers = Union[
    Controller,
    BackgroundTask,
    ClassController,
    Type[ClassController],
    Sequence[
        Union[
            Controller, BackgroundTask, ClassController, Type[ClassController],
        ]
    ],
    Any,
]


def appdaora(
    controllers: Controllers,
    middlewares: Optional[Middlewares] = None,
    options: bool = False,
    logger: Logger = getLogger(__name__),
) -> ASGIApp:
    routes = []
    func_controllers: List[Union[Controller, BackgroundTask]] = []
    path_methods_map: DefaultDict[str, List[MethodType]] = defaultdict(list)

    def update_path_methods_map(routes: Sequence[Route]) -> None:
        for route in routes:
            path_methods_map[route.path_pattern].append(route.method)

    def update_path_methods_map_with_route(routes: Sequence[Route]) -> None:
        for route in routes:
            if route.has_options:
                path_methods_map[route.path_pattern].append(route.method)

    if not isinstance(controllers, Sequence):
        controllers = [controllers]

    for controller in controllers:
        if (
            isinstance(controller, ClassController)
            or (
                isinstance(controller, type)
                and issubclass(controller, ClassController)
            )
            or (hasattr(controller, 'path'))
        ):
            routes.extend(get_class_routes(controller))
        else:
            func_controllers.append(controller)  # type: ignore

    for controller in func_controllers:
        if isinstance(controller, BackgroundTask):
            routes.extend(controller.create.routes)
            routes.extend(controller.get_results.routes)
            if options:
                update_path_methods_map(controller.create.routes)
                update_path_methods_map(controller.get_results.routes)
            else:
                update_path_methods_map_with_route(controller.create.routes)
                update_path_methods_map_with_route(
                    controller.get_results.routes
                )

        else:
            routes.extend(controller.routes)
            if options:
                update_path_methods_map(controller.routes)
            else:
                update_path_methods_map_with_route(controller.routes)

        for path, methods in path_methods_map.items():
            controller_ = make_options_controller(methods)
            routes.append(
                make_route(
                    path,
                    MethodType.OPTIONS,
                    controller_,
                    has_content_length=False,
                )
            )

    return asgi_app(
        make_router(routes, middlewares=middlewares, logger=logger)
    )


def get_class_routes(controller: Any) -> List[Route]:
    if isinstance(controller, type):
        controller = controller()

    return [
        make_route(
            path_pattern=controller.path,
            method=method,
            controller=getattr(controller, method_str),
        )
        for method in MethodType
        if hasattr(controller, method_str := method.value.lower())  # noqa
    ]
