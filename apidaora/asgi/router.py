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

from .base import ASGICallable


@dataclass
class Route:
    path_pattern: str
    method: MethodType
    controller: ASGICallable
    has_path_args: bool = False
    has_query: bool = False
    has_headers: bool = False
    has_body: bool = False


@dataclass
class ResolvedRoute:
    route: Route
    path_args: Dict[str, Any]
    path: str


@dataclass
class RoutesTreeRegex:
    name: str
    compiled_re: Optional[Pattern[Any]]


class RoutesTree(DefaultDict[str, Any]):
    regex: Optional[RoutesTreeRegex] = None

    def __init__(self) -> None:
        super().__init__(RoutesTree)


PATH_RE = re.compile(r'\{(?P<name>[^/:]+)(:(?P<pattern>[^/:]+))?\}')


def make_router(
    routes: Iterable[Route],
) -> Callable[[str, str], ResolvedRoute]:
    routes_tree = RoutesTree()

    for route in routes:
        path_pattern_parts = split_path(route.path_pattern)
        routes_tree_tmp = routes_tree

        for path_pattern_part in path_pattern_parts:
            match = PATH_RE.match(path_pattern_part)

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

    def route_(path: str, method: str) -> ResolvedRoute:
        path_parts = split_path(path)
        path_args = {}
        routes_tree_ = routes_tree

        for path_part in path_parts:
            if path_part in routes_tree_:
                routes_tree_ = routes_tree_[path_part]
                continue

            if routes_tree_.regex:
                compiled_re = routes_tree_.regex.compiled_re
                match = compiled_re.match(path_part) if compiled_re else None

                if not match and compiled_re:
                    raise PathNotFoundError(path)

                path_args[routes_tree_.regex.name] = path_part
                routes_tree_ = routes_tree_[routes_tree_.regex.name]

                continue

            raise PathNotFoundError(path)

        if method not in routes_tree_:
            raise MethodNotFoundError(method, path)

        return ResolvedRoute(
            route=routes_tree_[method], path_args=path_args, path=path
        )

    return route_


def split_path(path: str) -> Iterable[str]:
    return path.strip(' /').split('/')
