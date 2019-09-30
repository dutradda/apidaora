from typing import Dict, Iterable

from .router import Route, ResolvedRoute, Caller, split_path
from ..exceptions import MethodNotFoundError, PathNotFoundError


RoutesDict = Dict[str, Dict[str, Caller]]

EMPTY_PATH_ARGS = {}


def make_router(routes: Iterable[Route]) -> RoutesDict:
    routes_dict: RoutesDict = {}

    for route in routes:
        methods = routes_dict.get(route.path_pattern, {})
        methods[route.method.value] = route
        routes_dict[route.path_pattern] = methods    

    def route(path: str, method: str) -> ResolvedRoute:
        methods = routes_dict.get(path)

        if methods:
            route = methods.get(method)

            if route:
                return ResolvedRoute(route, EMPTY_PATH_ARGS, path)

            raise MethodNotFoundError(method)

        raise PathNotFoundError(path)

    return route
