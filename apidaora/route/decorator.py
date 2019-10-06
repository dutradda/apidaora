import functools
from typing import Any, Callable

from ..asgi.base import ASGICallable
from ..exceptions import MethodNotFoundError
from ..method import MethodType
from .factory import make_route


class _RouteDecorator:
    def __getattr__(self, attr_name: str) -> Any:
        if attr_name == '__name__':
            return type(self).__name__

        method = attr_name.upper()

        if method not in MethodType.__members__:
            raise MethodNotFoundError(attr_name)

        def decorator(
            path_pattern: str,
        ) -> Callable[[Callable[..., Any]], ASGICallable]:
            @functools.wraps(make_route)
            def wrapper(controller: Callable[..., Any]) -> ASGICallable:
                route = make_route(
                    path_pattern, MethodType[method], controller
                )
                return route.controller  # type: ignore

            return wrapper

        return decorator


route = _RouteDecorator()
