from typing import Optional, TypedDict, Union

from jsondaora import integer, jsondaora, string

from apidaora import (
    JSONRequestBody,
    JSONResponse,
    MethodType,
    appdaora,
    header_param,
    path,
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


async def hello_you_message(you: You, location: str) -> HelloMessage:
    return HelloMessage(
        message=await hello_message(you['name'], location), about_you=you
    )


async def hello_message(name: str, location: str) -> str:
    return f'Hello {name}! Welcome to {location}!'


# Application


@jsondaora
class RequestBody(JSONRequestBody):
    Content = TypedDict('Content', {'last_name': str, 'age': str})
    content: Content


@jsondaora
class Response(JSONResponse):
    Headers = TypedDict('Headers', {'x_req_id': int})
    headers: Headers
    body: Union[HelloMessage, str]


@path('/hello/{name}', MethodType.PUT)
async def controller(
    name: str,
    location: string(max_length=100),
    req_id: header_param(schema=Optional[int], name='x-req-id'),
    queries: Optional[str] = None,
    body: Optional[RequestBody] = None,
) -> Response:
    if body:
        message = await hello_you_message(
            You(
                name=name,
                last_name=body.content['last_name'],
                age=body.content['age'],
                location=location,
            ),
            location,
        )

    else:
        message = await hello_message(name, location)

    return Response(body=message, headers=Response.Headers(x_req_id=req_id))


app = appdaora(operations=[controller])
