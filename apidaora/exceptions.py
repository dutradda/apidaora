from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

from .header import _Header


class APIDaoraError(Exception):
    ...


class MethodNotFoundError(APIDaoraError):
    ...


class PathNotFoundError(APIDaoraError):
    ...


class InvalidReturnError(APIDaoraError):
    def __str__(self) -> str:
        return (
            f"handler_name='{self.args[1].__name__}', "
            f"return_type='{type(self.args[0]).__name__}', "
            f"return_value='{self.args[0]}'"
        )


@dataclass
class BadRequestError(APIDaoraError):
    name: str
    info: Dict[str, Any]
    headers: Optional[Sequence[_Header]] = None

    def __str__(self) -> str:
        return f"name='{self.name}', info={self.info}"

    @property
    def dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'info': self.info}


class InvalidTasksRepositoryError(APIDaoraError):
    ...


class InvalidRouteArgumentsError(APIDaoraError):
    ...
