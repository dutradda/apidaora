from typing import Any, Callable, Dict, Iterable

from ..exceptions import MethodNotFoundError, PathNotFoundError
from .router import ResolvedRoute, Route


RoutesDict = Dict[str, Dict[str, Route]]

EMPTY_PATH_ARGS: Dict[str, Any] = {}


def make_router(
    routes: Iterable[Route]
) -> Callable[[str, str], ResolvedRoute]:
    routes_dict: RoutesDict = {}

    for route in routes:
        methods = routes_dict.get(route.path_pattern, {})
        methods[route.method.value] = route
        routes_dict[route.path_pattern] = methods

    def route_(path: str, method: str) -> ResolvedRoute:
        methods = routes_dict.get(path)

        if methods:
            route = methods.get(method)

            if route:
                return ResolvedRoute(route, EMPTY_PATH_ARGS, path)

            raise MethodNotFoundError(method)

        raise PathNotFoundError(path)

    return route_
