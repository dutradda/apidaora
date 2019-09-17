from dataclasses import dataclass
from http import HTTPStatus

from dataclassesjson import dataclassjson, integer, string

from dataclassesapi import App, MethodType, Route
from dataclassesapi.request import Body, Headers, PathArgs, Query, Request
from dataclassesapi.response import Body as ResponseBody
from dataclassesapi.response import Response


@dataclass
class MyPathArgs(PathArgs):
    name: str


@dataclass
class MyQuery(Query):
    location: str


@dataclass
class MyHeaders(Headers):
    x_req_id: str


@dataclass
class MyBody(Body):
    last_name: str
    age: int


@dataclass
class MyRequest(Request):
    path_args: MyPathArgs
    query: MyQuery
    headers: MyHeaders
    body: MyBody


@dataclass
class You:
    name: str
    last_name: str
    location: string(max_length=100)
    age: integer(minimum=18)


@dataclass
class MyResponseBody(ResponseBody):
    hello_message: str
    about_you: You


@dataclassjson
@dataclass
class MyResponse(Response):
    body: MyResponseBody
    headers: MyHeaders


def hello_controller(req: MyRequest) -> MyResponse:
    body = MyResponseBody(
        hello_message=hello_message(req.path_args.name, req.query.location),
        about_you=You(
            name=req.path_args.name,
            last_name=req.body.last_name,
            location=req.query.location,
            age=req.body.age,
        ),
    )
    headers = MyHeaders(x_req_id=req.headers.x_req_id)
    return MyResponse(HTTPStatus.OK, body=body, headers=headers)


def hello_message(name: str, location: str) -> str:
    return f'Hello {name}! Welcome to {location}!'


class MyApp(App):
    _routes = (Route('/hello/{name}', MethodType.PUT, hello_controller),)


app = MyApp()
