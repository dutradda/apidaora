from dataclasses import dataclass

from ...core.router import Route
from ..spec import OpenAPIMethod


@dataclass
class PartialPath:
    method: OpenAPIMethod
    route: Route
