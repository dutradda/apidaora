from typing import TypedDict

from jsondaora import integer, jsondaora, string

from apidaora import appdaora, header, route


Age = header(type=int)


@jsondaora
class You(TypedDict):
    name: str
    last_name: str
    location: string(max_length=100)
    age: integer(minimum=18)


@jsondaora
class ReqBody(TypedDict):
    last_name: str


@jsondaora
class HelloOutput(TypedDict):
    hello_message: str
    abot_you: You


@route.put('/hello/{name}')
async def hello_controller(
    name: str, location: str, age: Age, body: ReqBody
) -> HelloOutput:
    you = You(name=name, location=location, age=age, **body)
    return HelloOutput(
        hello_message=await hello_message(name, location), about_you=you
    )


async def hello_message(name: str, location: str) -> str:
    return f'Hello {name}! Welcome to {location}!'


app = appdaora(hello_controller)
