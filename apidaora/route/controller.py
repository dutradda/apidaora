from abc import ABC, abstractmethod

from ..asgi.base import (
    ASGIBody,
    ASGICallableResults,
    ASGIHeaders,
    ASGIPathArgs,
    ASGIQueryDict,
)
from ..asgi.router import Route


class Controller(ABC):
    route: Route

    @abstractmethod
    def __call__(
        self,
        path_args: ASGIPathArgs,
        query_dict: ASGIQueryDict,
        headers: ASGIHeaders,
        body: ASGIBody,
    ) -> ASGICallableResults:
        ...
