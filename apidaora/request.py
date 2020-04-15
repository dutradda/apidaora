from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type

from .header import Header
from .route.controller_input import ControllerInput


@dataclass
class Request:
    path_pattern: str
    resolved_path: str
    controller_input_cls: Type[ControllerInput]
    path_args: Optional[Dict[str, Any]] = None
    query_dict: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Header]] = None
    body: Any = None
    ctx: Dict[str, Any] = field(default_factory=dict)


def make_controller_input_from_request(request: Request) -> ControllerInput:
    kwargs = {}

    if request.path_args:
        kwargs.update(request.path_args)
    if request.query_dict:
        kwargs.update(request.query_dict)
    if request.headers:
        kwargs.update(request.headers)
    if request.body:
        kwargs['body'] = request.body
    if request.controller_input_cls.__annotations_info__.has_kwargs:
        kwargs.update(request.ctx)
        kwargs['request'] = request

    return request.controller_input_cls(**kwargs)
