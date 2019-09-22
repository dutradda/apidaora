# apidaora

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/apidaora">
    <img src="https://dutradda.github.io/apidaora/apidaora.svg" alt="apidaora" width="300"/>
  </a>
</p>

<p align="center">
    <em>OpenAPI / HTTP / REST API using <b>dataclasses</b> and <b>TypedDict</b> annotation for python</b></em>
</p>

---

**Documentation**: <a href="https://dutradda.github.io/apidaora" target="_blank">https://dutradda.github.io/apidaora</a>

**Source Code**: <a href="https://github.com/dutradda/apidaora" target="_blank">https://github.com/dutradda/apidaora</a>

---


## Key Features

- Declare request objects as @jsondaora (can be TypedDict or @dataclass)
- Declare response objects as @jsondaora (can be TypedDict or @dataclass)


## Requirements

 - Python 3.7+
 - [jsondaora](https://github.com/dutradda/jsondaora) for json validation/parsing
 - [orjson](https://github.com/ijl/orjson) for json/bytes serialization (jsondaora dependency)


## Instalation
```
$ pip install apidaora
```


## Basic example

```python
from dataclasses import dataclass

from apidaora import JSONResponse, MethodType, app_daora, path


@dataclass
class Response(JSONResponse):
    body: str


@path('/hello', MethodType.GET)
def controller(name: str) -> Response:
    message = f'Hello {name}!'
    return Response(body=message)


app = app_daora(operations=[controller])

```

Running the server (needs uvicorn [installed](https://www.uvicorn.org)):

```bash
uvicorn myapp:app

```

```
INFO: Started server process [16220]
INFO: Waiting for application startup.
INFO: ASGI 'lifespan' protocol appears unsupported.
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

```

Quering the server (needs curl [installed](https://curl.haxx.se/docs/install.html)):

```bash
curl -i localhost:8000/hello?name=World

```

```
HTTP/1.1 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 14

"Hello World!"

```


## Example for more request/response details

```python
from typing import Optional, TypedDict, Union

from jsondaora import integer, jsondaora, string

from apidaora import (
    JSONRequestBody,
    JSONResponse,
    MethodType,
    app_daora,
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


def hello_you_message(you: You, location: str) -> HelloMessage:
    return HelloMessage(
        message=hello_message(you['name'], location), about_you=you
    )


def hello_message(name: str, location: str) -> str:
    return f'Hello {name}! Welcome to {location}!'


# Application


@jsondaora
class RequestBody(JSONRequestBody):
    class Content(TypedDict):
        last_name: str
        age: str

    content: Content


@jsondaora
class Response(JSONResponse):
    class Headers(TypedDict):
        x_req_id: int

    headers: Headers
    body: Union[HelloMessage, str]


@path('/hello/{name}', MethodType.PUT)
def controller(
    name: str,
    location: string(max_length=100),
    req_id: header_param(schema=Optional[int], name='x-req-id'),
    body: Optional[RequestBody] = None,
) -> Response:
    if body:
        message = hello_you_message(
            You(
                name=name,
                last_name=body.content['last_name'],
                age=body.content['age'],
                location=location,
            ),
            location,
        )

    else:
        message = hello_message(name, location)

    return Response(body=message, headers=Response.Headers(x_req_id=req_id))


app = app_daora(operations=[controller])

```

Running the server:

```bash
uvicorn myapp:app

```

```
INFO: Started server process [16220]
INFO: Waiting for application startup.
INFO: ASGI 'lifespan' protocol appears unsupported.
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

```

Quering the server:

```bash
curl -i -X PUT localhost:8000/hello/Me?location=World \
    -H 'x-req-id: 1243567890' \
    -d '{"last_name":"My Self","age":32}'

```

```
HTTP/1.1 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
x-req-id: 1243567890
content-type: application/json
content-length: 117

{"message":"Hello Me! Welcome to World!","about_you":{"name":"Me","last_name":"My Self","age":32,"location":"World"}}

```
