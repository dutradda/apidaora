from http import HTTPStatus

from jsondaora import jsondaora

from apidaora import MethodType, Route, asgi_app
from apidaora.request import Query, Request
from apidaora.response import Body as ResponseBody
from apidaora.response import Response


@jsondaora
class MyQuery(Query):
    name: str


@jsondaora
class MyRequest(Request):
    query: MyQuery


@jsondaora
class MyResponseBody(ResponseBody):
    message: str


@jsondaora
class MyResponse(Response):
    body: MyResponseBody


def hello_controller(req: MyRequest) -> MyResponse:
    name = req.query['name']
    body = MyResponseBody(message=f'Hello {name}!')
    return MyResponse(HTTPStatus.OK, body=body)


app = asgi_app([Route('/hello', MethodType.GET, hello_controller)])
