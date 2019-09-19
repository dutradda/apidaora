# apidaora

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/apidaora">
    <img src="apidaora.svg" alt="apidaora" width="300"/>
  </a>
</p>

<p align="center">
    <em>Asgi App using typing annotation</b></em>
</p>

---

**Documentation**: <a href="https://dutradda.github.io/apidaora" target="_blank">https://dutradda.github.io/apidaora</a>

**Source Code**: <a href="https://github.com/dutradda/apidaora" target="_blank">https://github.com/dutradda/apidaora</a>

---


## Key Features

- Declare request object as @dataclass:
    + `PathArgs` for values on path
    + `Query` for values on query string
    + `Headers` for values on headers
    + `Body` for values on body

- Declare response object as @dataclass:
    + `Headers` for values on headers
    + `Body` for values on body


## Requirements

 - Python 3.7+
 - [typingjson](https://github.com/dutradda/typingjson) for json validation/parsing
 - [orjson](https://github.com/ijl/orjson) for json/bytes serialization


## Instalation
```
$ pip install apidaora
```


## Basic example

```python
from http import HTTPStatus

from typingjson import typingjson

from apidaora import MethodType, Route, asgi_app
from apidaora.request import Query, Request
from apidaora.response import Body as ResponseBody
from apidaora.response import Response


@typingjson
class MyQuery(Query):
    name: str


@typingjson
class MyRequest(Request):
    query: MyQuery


@typingjson
class MyResponseBody(ResponseBody):
    message: str


@typingjson
class MyResponse(Response):
    body: MyResponseBody


def hello_controller(req: MyRequest) -> MyResponse:
    name = req.query['name']
    body = MyResponseBody(message=f'Hello {name}!')
    return MyResponse(HTTPStatus.OK, body=body)


app = asgi_app([Route('/hello', MethodType.GET, hello_controller)])

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
content-length: 26

{"message":"Hello World!"}

```


## Example for complete request/response

```python
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
    -H 'x-req-id: 1a2b3c4d5e6f7g8h' \
    -d '{"last_name":"My Self","age":32}'

```

```
HTTP/1.1 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
x-req-id: 1a2b3c4d5e6f7g8h
content-type: application/json
content-length: 123

{"hello_message":"Hello Me! Welcome to World!","about_you":{"name":"Me","last_name":"My Self","location":"World","age":32}}

```
