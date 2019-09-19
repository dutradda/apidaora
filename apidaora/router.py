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

from apidaora.exceptions import MethodNotFoundError, PathNotFoundError
from apidaora.method import MethodType
from apidaora.request import Request
from apidaora.response import Response


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


def router(routes: Iterable[Route]) -> RoutesTree:
    routes_tree = RoutesTree()
    path_regex = re.compile(r'\{(?P<name>[^/:]+)(:(?P<pattern>[^/:]+))?\}')

    for route in routes:
        path_pattern_parts = _split_path(route.path_pattern)
        routes_tree_tmp = routes_tree

        for path_pattern_part in path_pattern_parts:
            match = path_regex.match(path_pattern_part)

            if match:
                group = match.groupdict()
                pattern = group.get('pattern')
                regex: Optional[Pattern[Any]] = re.compile(
                    pattern
                ) if pattern else None

                routes_tree_tmp.regex = RoutesTreeRegex(
                    group['name'], compiled_re=regex
                )
                routes_tree_tmp = routes_tree_tmp[routes_tree_tmp.regex.name]

                continue

            routes_tree_tmp = routes_tree_tmp[path_pattern_part]

        routes_tree_tmp[route.method.value] = route

    return routes_tree


def route(routes_tree: RoutesTree, path: str, method: str) -> ResolvedRoute:
    path_parts = _split_path(path)
    path_args = {}

    for path_part in path_parts:
        if path_part in routes_tree:
            routes_tree = routes_tree[path_part]
            continue

        if routes_tree.regex:
            compiled_re = routes_tree.regex.compiled_re
            match = compiled_re.match(path_part) if compiled_re else None

            if not match and compiled_re:
                raise PathNotFoundError(path)

            path_args[routes_tree.regex.name] = path_part
            routes_tree = routes_tree[routes_tree.regex.name]

            continue

        raise PathNotFoundError(path)

    if method not in routes_tree:
        raise MethodNotFoundError(method, path)

    return ResolvedRoute(
        route=routes_tree[method], path_args=path_args, path=path
    )


def _split_path(path: str) -> Iterable[str]:
    return path.strip(' /').split('/')
