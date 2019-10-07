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

- Declaration of request/response as dataclasses and dicts using typing annotations
- Input data validation with [jsondaora](https://github.com/dutradda/jsondaora)
- One of the [fastest](#benchmark) python api framework
- Can run on any asgi server


## Requirements

 - Python 3.8+
 - [jsondaora](https://github.com/dutradda/jsondaora) for json validation/parsing
 - [orjson](https://github.com/ijl/orjson) for json/bytes serialization (jsondaora dependency)


## Instalation
```
$ pip install apidaora
```


## Simple example

```python
from apidaora import appdaora, route


@route.get('/hello')
def hello_controller(name: str):
    return f'Hello {name}!'


app = appdaora(hello_controller)

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


## Basic example

```python
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
    -H 'x-age: 32' \
    -d '{"last_name":"My Self"}'

```

```
HTTP/1.1 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 123

{"hello_message":"Hello Me! Welcome to World!","about_you":{"name":"Me","location":"World","age":32,"last_name":"My Self"}}

```


## Example for more request/response details

```python
from http import HTTPStatus

from jsondaora import jsondaora

from apidaora import BadRequestError, JSONResponse, appdaora, header, route


# Domain layer, here are the domain related definitions
# it is apidaora/framework/http independent


@jsondaora
class You:
    name: str
    last_name: str
    age: int


DB = {}


def add_you(you):
    if you.name in DB:
        raise YouAlreadyBeenAddedError(you.name)
    DB[you.name] = you


def get_you(name):
    try:
        return DB[name]
    except KeyError:
        raise YouWereNotFoundError(name)


class DBError(Exception):
    @property
    def info(self):
        return {'name': self.args[0]}


class YouAlreadyBeenAddedError(DBError):
    name = 'you-already-been-added'


class YouWereNotFoundError(DBError):
    name = 'you-were-not-found'


# Application layer, here are the http related definitions

# See: https://dutrdda.github.io/apidaora/tutorial/headers/
ReqID = header(type=str, http_name='http_req_id')


@route.post('/you/')
async def add_you_controller(req_id: ReqID, body: You) -> JSONResponse:
    try:
        add_you(body)
    except YouAlreadyBeenAddedError as error:
        raise BadRequestError(name=error.name, info=error.info) from error

    return JSONResponse(body=body, status=HTTPStatus.CREATED, headers=[req_id])


@route.get('/you/{name}')
async def get_you_controller(name: str, req_id: ReqID) -> JSONResponse:
    try:
        return JSONResponse(get_you(name), headers=[req_id])
    except YouWereNotFoundError as error:
        raise BadRequestError(name=error.name, info=error.info) from error


app = appdaora([add_you_controller, get_you_controller])

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
curl -X POST -i localhost:8000/you/ -H 'http_req_id: 1a2b3c4d' -d '{"name":"Me","last_name":"Myself","age":32}'

```

```
HTTP/1.1 201 Created
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 43

{"name":"Me","last_name":"Myself","age":32}

```


## Benchmark

![techempower benchmark](https://dutradda.github.io/apidaora/benchmark.png "TechEmpower Frameworks Benchmark")

The full results can be found [here](https://www.techempower.com/benchmarks/#section=test&runid=76bbd357-a161-42eb-a203-051bdd949006&hw=ph&test=query&l=zijzen-v)
