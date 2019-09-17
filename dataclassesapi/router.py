import re
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    Optional,
    Pattern,
)

from dataclassesapi.exceptions import MethodNotFoundError, PathNotFoundError
from dataclassesapi.method import MethodType
from dataclassesapi.request import Request
from dataclassesapi.response import Response


@dataclass
class RoutesTreeRegex:
    name: str
    compiled_re: Optional[Pattern[Any]]


class RoutesTree(DefaultDict[str, Any]):
    regex: Optional[RoutesTreeRegex] = None

    def __init__(self) -> None:
        super().__init__(RoutesTree)


@dataclass
class Route:
    path_pattern: str
    method: MethodType
    caller: Callable[[Request], Response]


@dataclass
class ResolvedRoute:
    route: Route
    path_args: Dict[str, Any]
    path: str


class Router:
    def __init__(self) -> None:
        self._routes_tree = RoutesTree()
        self._regex = re.compile(
            r'\{(?P<name>[^/:]+)(:(?P<pattern>[^/:]+))?\}'
        )

    def add_routes(self, routes: Iterable[Route]) -> None:
        routes_tree = self._routes_tree

        for route in routes:
            path_pattern_parts = split_path(route.path_pattern)

            for path_pattern_part in path_pattern_parts:
                match = self._regex.match(path_pattern_part)

                if match:
                    group = match.groupdict()
                    pattern = group.get('pattern')
                    regex: Optional[Pattern[Any]] = re.compile(
                        pattern
                    ) if pattern else None

                    routes_tree.regex = RoutesTreeRegex(
                        group['name'], compiled_re=regex
                    )
                    routes_tree = routes_tree[routes_tree.regex.name]

                    continue

                routes_tree = routes_tree[path_pattern_part]

            routes_tree[route.method.value] = route

    def route(self, path: str, method: str) -> ResolvedRoute:
        routes = self._routes_tree
        path_parts = split_path(path)
        path_args = {}

        for i, path_part in enumerate(path_parts):
            if path_part in routes:
                routes = routes[path_part]
                continue

            if routes.regex:
                compiled_re = routes.regex.compiled_re
                match = compiled_re.match(path_part) if compiled_re else None

                if not match and compiled_re:
                    raise PathNotFoundError(path)

                path_args[routes.regex.name] = path_part
                routes = routes[routes.regex.name]

                continue

            raise PathNotFoundError(path)

        if method not in routes:
            raise MethodNotFoundError(path, method)

        return ResolvedRoute(
            route=routes[method], path_args=path_args, path=path
        )


def split_path(path: str) -> Iterable[str]:
    return path.strip(' /').split('/')
