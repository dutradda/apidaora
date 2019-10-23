from typing import TypedDict

from jsondaora import IntegerField, StringField, jsondaora

from apidaora import Header, appdaora, route


class Integer(IntegerField, minimum=18):
    ...


class String(StringField, max_length=100):
    ...


class Age(Header, type=Integer):
    ...


@jsondaora
class You(TypedDict):
    name: str
    last_name: str
    location: str
    age: int


@jsondaora
class ReqBody(TypedDict):
    last_name: str


@jsondaora
class HelloOutput(TypedDict):
    hello_message: str
    about_you: You


@route.put('/hello/{name}')
async def hello_controller(
    name: str, location: String, age: Age, body: ReqBody
) -> HelloOutput:
    you = You(
        name=name,
        location=location.value,
        age=age.value.value,
        last_name=body['last_name'],
    )
    return HelloOutput(
        hello_message=await hello_message(name, location.value), about_you=you
    )


async def hello_message(name: str, location: str) -> str:
    return f'Hello {name}! Welcome to {location}!'


app = appdaora(hello_controller)
