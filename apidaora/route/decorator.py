from typing import Any, Callable, Union

from ..asgi.router import Controller
from ..controllers.background_task import BackgroundTask, make_background_task
from ..exceptions import InvalidRouteArgumentsError, MethodNotFoundError
from ..method import MethodType
from .factory import make_route


class _RouteDecorator:
    def __getattr__(
        self, attr_name: str
    ) -> Callable[
        ..., Callable[[Callable[..., Any]], Union[Controller, BackgroundTask]]
    ]:
        if attr_name == '__name__':
            return type(self).__name__  # type: ignore

        if attr_name == 'background':
            brackground = True

        else:
            brackground = False
            method = attr_name.upper()

            if method not in MethodType.__members__:
                raise MethodNotFoundError(attr_name)

        def decorator(
            path_pattern: str, **kwargs: Any
        ) -> Callable[[Callable[..., Any]], Union[Controller, BackgroundTask]]:
            if len(kwargs) > 0 and tuple(kwargs.keys()) != (
                'tasks_repository',
            ):
                raise InvalidRouteArgumentsError(kwargs)

            def wrapper(
                controller: Callable[..., Any]
            ) -> Union[Controller, BackgroundTask]:
                if brackground:
                    tasks_repository = kwargs.get('tasks_repository')
                    return make_background_task(
                        controller,
                        path_pattern,
                        tasks_repository=tasks_repository,
                    )

                else:
                    route = make_route(
                        path_pattern, MethodType[method], controller
                    )
                    return route.controller

            return wrapper

        return decorator


route = _RouteDecorator()
