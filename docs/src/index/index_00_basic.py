from http import HTTPStatus
from typing import TypedDict

from jsondaora import jsondaora

from apidaora import JSONResponse, MethodType, Request, Route, asgi_app


@jsondaora
class MyQuery(TypedDict):
    name: str


@jsondaora
class MyRequest(Request):
    query: MyQuery


@jsondaora
class MyResponseBody(TypedDict):
    message: str


@jsondaora
class MyResponse(JSONResponse):
    body: MyResponseBody


def hello_controller(req: MyRequest) -> MyResponse:
    name = req.query['name']
    body = MyResponseBody(message=f'Hello {name}!')
    return MyResponse(HTTPStatus.OK, body=body)


app = asgi_app([Route('/hello', MethodType.GET, hello_controller)])
