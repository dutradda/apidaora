import functools
from typing import Any, Callable, Union

from ..asgi.router import Controller
from ..controllers.background_task import BackgroundTask, make_background_task
from ..exceptions import MethodNotFoundError
from ..method import MethodType
from .factory import make_route


class _RouteDecorator:
    def __getattr__(self, attr_name: str) -> Any:
        if attr_name == '__name__':
            return type(self).__name__

        if attr_name == 'background':
            brackground = True

        else:
            brackground = False
            method = attr_name.upper()

            if method not in MethodType.__members__:
                raise MethodNotFoundError(attr_name)

        def decorator(
            path_pattern: str,
        ) -> Callable[[Callable[..., Any]], Controller]:
            @functools.wraps(make_route)
            def wrapper(
                controller: Callable[..., Any]
            ) -> Union[Controller, BackgroundTask]:
                if brackground:
                    return make_background_task(controller, path_pattern)

                else:
                    route = make_route(
                        path_pattern, MethodType[method], controller
                    )
                    return route.controller

            return wrapper

        return decorator


route = _RouteDecorator()
