from dataclasses import dataclass
from http import HTTPStatus

from dataclassesjson import dataclassjson

from apidaora import MethodType, Route, asgi_app
from apidaora.request import Query, Request
from apidaora.response import Body as ResponseBody
from apidaora.response import Response


@dataclass
class MyQuery(Query):
    name: str


@dataclass
class MyRequest(Request):
    query: MyQuery


@dataclass
class MyResponseBody(ResponseBody):
    message: str


@dataclassjson
@dataclass
class MyResponse(Response):
    body: MyResponseBody


def hello_controller(req: MyRequest) -> MyResponse:
    name = req.query.name
    body = MyResponseBody(message=f'Hello {name}!')
    return MyResponse(HTTPStatus.OK, body=body)


app = asgi_app([Route('/hello', MethodType.GET, hello_controller)])
