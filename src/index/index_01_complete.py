from http import HTTPStatus
from typing import TypedDict

from jsondaora import integer, jsondaora, string

from apidaora import JSONResponse, MethodType, Request, Route, asgi_app


@jsondaora
class MyPathArgs(TypedDict):
    name: str


@jsondaora
class MyQuery(TypedDict):
    location: str


@jsondaora
class MyHeaders(TypedDict):
    x_req_id: str


@jsondaora
class MyBody(TypedDict):
    last_name: str
    age: int


@jsondaora
class MyRequest(Request):
    path_args: MyPathArgs
    query: MyQuery
    headers: MyHeaders
    body: MyBody


# if the class is not a TypedDict, jsondaora
# will create a dataclass from it
@jsondaora
class You:
    name: str
    last_name: str
    location: string(max_length=100)
    age: integer(minimum=18)


@jsondaora
class MyResponseBody(TypedDict):
    hello_message: str
    about_you: You


@jsondaora
class MyResponse(JSONResponse):
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
