from http import HTTPStatus

from typingjson import integer, string, typingjson

from apidaora import MethodType, Route, asgi_app
from apidaora.request import Body, Headers, PathArgs, Query, Request
from apidaora.response import Body as ResponseBody
from apidaora.response import Response


@typingjson
class MyPathArgs(PathArgs):
    name: str


@typingjson
class MyQuery(Query):
    location: str


@typingjson
class MyHeaders(Headers):
    x_req_id: str


@typingjson
class MyBody(Body):
    last_name: str
    age: int


@typingjson
class MyRequest(Request):
    path_args: MyPathArgs
    query: MyQuery
    headers: MyHeaders
    body: MyBody


@typingjson
class You:
    name: str
    last_name: str
    location: string(max_length=100)
    age: integer(minimum=18)


@typingjson
class MyResponseBody(ResponseBody):
    hello_message: str
    about_you: You


@typingjson
class MyResponse(Response):
    body: MyResponseBody
    headers: MyHeaders


def hello_controller(req: MyRequest) -> MyResponse:
    body = MyResponseBody(
        hello_message=hello_message(
            req.path_args['name'], req.query['location']
        ),
        about_you=You(
            name=req.path_args['name'],
            last_name=req.body['last_name'],
            location=req.query['location'],
            age=req.body['age'],
        ),
    )
    headers = MyHeaders(x_req_id=req.headers['x_req_id'])
    return MyResponse(HTTPStatus.OK, body=body, headers=headers)


def hello_message(name: str, location: str) -> str:
    return f'Hello {name}! Welcome to {location}!'


app = asgi_app([Route('/hello/{name}', MethodType.PUT, hello_controller)])
