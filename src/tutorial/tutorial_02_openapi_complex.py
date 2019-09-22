from http import HTTPStatus
from typing import Optional, TypedDict

from jsondaora import integer, jsondaora, string

from apidaora import (
    ContentType,
    MethodType,
    Path,
    header_param,
    openapi_app,
    path_param,
    query_param,
    response_headers,
)


# Domain


@jsondaora
class You(TypedDict):
    name: str
    last_name: str
    age: integer(minimum=18)


@jsondaora
class HelloMessage(TypedDict):
    message: str
    about_you: You


def hello_message(you: You, location: str) -> HelloMessage:
    return HelloMessage(
        message=f'Hello {you.name}! Welcome to {location}!', about_you=you
    )


# Application


@jsondaora
class RequestBody:
    class Content(TypedDict):
        last_name: str
        age: str

    content_type = ContentType.APPLICATION_JSON
    content: Content


@jsondaora
class Response:
    status_code = HTTPStatus.OK
    content_type = ContentType.APPLICATION_JSON
    Headers = response_headers(x_req_id=int)
    headers: Headers
    body: HelloMessage


def controller(
    name: path_param(schema=str),
    location: query_param(schema=string(max_length=100), required=True),
    req_id: header_param(schema=int, name='x-req-id'),
    body: Optional[RequestBody] = None,
) -> Response:
    content = body.content
    message = hello_message(
        You(name=name, last_name=content.last_name, age=content.age), location
    )
    return Response(body=message, headers=Response.Headers(x_req_id=req_id))


path = Path(
    pattern='/hello',
    method=MethodType.PUT,
    operation=controller,
    responses=[Response],
)


app = openapi_app(paths=[path])
