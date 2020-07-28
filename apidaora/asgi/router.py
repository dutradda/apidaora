import dataclasses
import re
from abc import ABC, abstractmethod
from functools import lru_cache
from logging import Logger
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Pattern,
    Tuple,
    Union,
)

from apidaora.exceptions import (
    InvalidPathError,
    MethodNotFoundError,
    PathNotFoundError,
)
from apidaora.method import MethodType

from ..middlewares import Middlewares
from .base import (
    ASGIBody,
    ASGICallableResults,
    ASGIHeaders,
    ASGIPathArgs,
    ASGIQueryDict,
)
from .request import AsgiRequest


class Controller(ABC):
    routes: List['Route']
    middlewares: Optional[Middlewares] = None
    logger: Optional[Logger] = None

    @abstractmethod
    def __call__(self, request: AsgiRequest) -> ASGICallableResults:
        ...


ControllerAnnotation = Callable[
    [ASGIPathArgs, ASGIQueryDict, ASGIHeaders, ASGIBody], ASGICallableResults
]


@dataclasses.dataclass
class Route:
    path_pattern: str
    method: MethodType
    controller: Controller
    has_path_args: bool = False
    has_query: bool = False
    has_headers: bool = False
    has_body: bool = False
    has_options: bool = False


@dataclasses.dataclass
class ResolvedRoute:
    route: Route
    path_args: Dict[str, Any]
    path: str


@dataclasses.dataclass
class RoutesTreeRegex:
    name: str
    compiled_re: Optional[Pattern[Any]]


class RoutesTree(DefaultDict[str, Any]):
    regex: Optional[RoutesTreeRegex] = None

    def __init__(self) -> None:
        super().__init__(RoutesTree)


PATH_RE = re.compile(r'\{(?P<name>[^/:]+)(:(?P<pattern>[^/:]+))?\}')


def make_router(
    routes: Union[List[Route], Tuple[Route]],
    middlewares: Optional[Middlewares] = None,
    logger: Optional[Logger] = None,
) -> Callable[[str, str], ResolvedRoute]:
    has_regex_path = False

    for route in routes:
        if '{' in route.path_pattern and '}' in route.path_pattern:
            has_regex_path = True
            break

        elif '{' in route.path_pattern or '}' in route.path_pattern:
            raise InvalidPathError(route.path_pattern)

        if logger:
            route.controller.logger = logger

    if has_regex_path:
        return make_tree_router(routes, middlewares)

    return make_dict_router(routes, middlewares)


def make_tree_router(
    routes: Iterable[Route], middlewares: Optional[Middlewares] = None,
) -> Callable[[str, str], ResolvedRoute]:
    routes_tree = RoutesTree()

    for route in routes:
        set_middlewares_route(route, middlewares)
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

    @lru_cache(maxsize=1024 * 1024)
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


def make_dict_router(
    routes: Iterable[Route], middlewares: Optional[Middlewares] = None,
) -> Callable[[str, str], ResolvedRoute]:
    routes_dict = {}

    for route in routes:
        set_middlewares_route(route, middlewares)
        path = route.path_pattern.strip(STRIP_VALUES)
        routes_dict[(path, route.method.value)] = ResolvedRoute(
            route, {}, path
        )

    def route_(path: str, method: str) -> ResolvedRoute:
        try:
            return routes_dict[(path.strip(STRIP_VALUES), method)]

        except KeyError:
            if any([path in k for k in routes_dict.keys()]):
                raise MethodNotFoundError(method, path)

            raise PathNotFoundError(path)

    return route_


def set_middlewares_route(
    route: Route, middlewares: Optional[Middlewares]
) -> None:
    if middlewares:
        if (
            not hasattr(route.controller, 'middlewares')
            or not route.controller.middlewares
        ):
            route.controller.middlewares = Middlewares(
                pre_execution=middlewares.pre_execution,
                post_execution=middlewares.post_execution,
            )
        else:
            route_middlewares = Middlewares(
                pre_execution=route.controller.middlewares.pre_execution,
                post_execution=route.controller.middlewares.post_execution,
            )
            route_middlewares.pre_execution.extend(middlewares.pre_execution)
            route_middlewares.post_execution.extend(middlewares.post_execution)
            route.controller.middlewares = route_middlewares


def split_path(path: str) -> Iterable[str]:
    return path.strip(STRIP_VALUES).split('/')


STRIP_VALUES = ' /'
