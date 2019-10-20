from typing import Any, Callable

from ..asgi.router import ControllerAnnotation, Route
from ..exceptions import MethodNotFoundError
from ..method import MethodType


class _RouteDecorator:
    def __getattr__(self, attr_name: str) -> Any:
        if attr_name == '__name__':
            return type(self).__name__

        method = attr_name.upper()

        if method not in MethodType.__members__:
            raise MethodNotFoundError(attr_name)

        def decorator(
            path_pattern: str,
            query: bool = False,
            headers: bool = False,
            body: bool = False,
        ) -> Callable[[ControllerAnnotation], ControllerAnnotation]:
            if '{' in path_pattern and '}' in path_pattern:
                has_path_args = True
            else:
                has_path_args = False

            def wrapper(
                controller: ControllerAnnotation,
            ) -> ControllerAnnotation:
                route = Route(
                    path_pattern=path_pattern,
                    method=MethodType[method],
                    controller=controller,  # type: ignore
                    has_path_args=has_path_args,
                    has_query=query,
                    has_headers=headers,
                    has_body=body,
                )
                controller.route = route  # type: ignore
                return controller

            return wrapper

        return decorator


route = _RouteDecorator()
