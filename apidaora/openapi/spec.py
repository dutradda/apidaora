# type: ignore

from http import HTTPStatus
from typing import (
    Any,
    Dict,
    Iterable,
    Optional,
    Type,
    TypedDict,
    Union,
    _GenericAlias,
)

from jsondaora import jsondaora

from ..content import ContentType
from ..method import MethodType
from .parameters import Parameter
from .security import Security, SecurityType


@jsondaora
class OpenAPIMethod(TypedDict):
    parameters: Iterable[Parameter]

    class Response(TypedDict):
        class Content(TypedDict):
            schema: Type[Any]

        content: Dict[ContentType, Content]

    responses: Dict[HTTPStatus, Response]
    security: Dict[SecurityType, Security]
    request_body: Optional[Type[Any]] = None
    operation_id: Optional[str] = None


ParameterName = str
SchemaName = str
PathPattern = str


@jsondaora
class OpenAPISpec(TypedDict):
    class Server(TypedDict):
        url: str
        description: str

    class Info(TypedDict):
        version: str
        title: str

    class Components(TypedDict):
        parameters: Dict[ParameterName, Parameter]
        security_schemes: Dict[SecurityType, Security]
        schemas: Dict[SchemaName, Type[Any]]

    openapi: str
    info: Info
    server: Server
    paths: Dict[PathPattern, Dict[MethodType, OpenAPIMethod]]


def get_operation_request_bodies(body_type):
    operation_bodies = {}

    if isinstance(body_type, _GenericAlias) and body_type.__origin__ is Union:
        for union_type in body_type.__args__:
            if not (union_type is type(None) or union_type is None):  # noqa
                content_type = union_type.__content_type__

                if isinstance(content_type, ContentType):
                    operation_bodies[content_type] = union_type

    else:
        content_type = body_type.__content_type__

        if isinstance(content_type, ContentType):
            operation_bodies[content_type] = body_type

    return operation_bodies
