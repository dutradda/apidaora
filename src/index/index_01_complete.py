from http import HTTPStatus
from typing import TypedDict

from jsondaora import integer, jsondaora, string

from apidaora import JSONResponse, MethodType, Request, Route, asgi_app


@jsondaora
class MyHeaders(TypedDict):
    x_req_id: str


@jsondaora
class MyRequest(Request):
    class MyPathArgs(TypedDict):
        name: str

    class MyQuery(TypedDict):
        location: str

    class MyBody(TypedDict):
        last_name: str
        age: int

    path_args: MyPathArgs
    query: MyQuery
    headers: MyHeaders
    body: MyBody


@jsondaora
class MyResponse(JSONResponse):
    class You:
        name: str
        last_name: str
        location: string(max_length=100)
        age: integer(minimum=18)

    class MyResponseBody(TypedDict):
        hello_message: str
        about_you: 'MyResponse.You'

    body: MyResponseBody
    headers: MyHeaders


def hello_controller(req: MyRequest) -> MyResponse:
    body = MyResponse.MyResponseBody(
        hello_message=hello_message(
            req.path_args['name'], req.query['location']
        ),
        about_you=MyResponse.You(
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
