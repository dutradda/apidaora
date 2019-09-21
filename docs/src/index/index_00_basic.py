from http import HTTPStatus
from typing import TypedDict

from jsondaora import jsondaora

from apidaora import JSONResponse, MethodType, Request, Route, asgi_app


@jsondaora
class MyRequest(Request):
    class MyQuery(TypedDict):
        name: str

    query: MyQuery


@jsondaora
class MyResponse(JSONResponse):
    class MyResponseBody(TypedDict):
        message: str

    body: MyResponseBody


def hello_controller(req: MyRequest) -> MyResponse:
    name = req.query['name']
    body = MyResponse.MyResponseBody(message=f'Hello {name}!')
    return MyResponse(HTTPStatus.OK, body=body)


app = asgi_app([Route('/hello', MethodType.GET, hello_controller)])
