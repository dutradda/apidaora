from typing import TypedDict

from jsondaora import jsondaora

from apidaora import JSONResponse, MethodType
from apidaora.core.app import asgi_app
from apidaora.core.request import Request
from apidaora.core.router import Route


@jsondaora
class MyRequest(Request):
    MyQuery = TypedDict('MyQuery', {'name': str})
    query: MyQuery


@jsondaora
class MyResponse(JSONResponse):
    MyResponseBody = TypedDict('MyResponseBody', {'message': str})
    body: MyResponseBody


def hello_controller(req: MyRequest) -> MyResponse:
    name = req.query['name']
    body = MyResponse.MyResponseBody(message=f'Hello {name}!')
    return MyResponse(body=body)


app = asgi_app([Route('/hello', MethodType.GET, hello_controller)])
