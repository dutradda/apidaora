# mypy: ignore-errors

from http import HTTPStatus

import pytest
from asgi_testclient import TestClient
from jsondaora import integer, jsondaora, string

from apidaora import MethodType
from apidaora.core.app import asgi_app
from apidaora.core.headers import Headers
from apidaora.core.request import Body as RequestBody
from apidaora.core.request import PathArgs, Query, Request
from apidaora.core.response import Body as ResponseBody
from apidaora.core.response import JSONResponse
from apidaora.core.router import Route


@jsondaora
class FakePathArgs(PathArgs):
    id: int


@jsondaora
class FakeQuery(Query):
    query: int


@jsondaora
class FakeHeaders(Headers):
    x_header: float


@jsondaora
class FakeBody(RequestBody):
    string: str
    integer: int


@jsondaora
class FakeRequest(Request):
    path_args: FakePathArgs
    query: FakeQuery
    headers: FakeHeaders
    body: FakeBody


@jsondaora
class Faked:
    string: string(max_length=100)
    integer: integer(minimum=18)


@jsondaora
class FakeResponseBody(ResponseBody):
    faked: Faked


@jsondaora
class FakeResponse(JSONResponse):
    body: FakeResponseBody
    headers: FakeHeaders


def fake_controller(req: FakeRequest) -> FakeResponse:
    return FakeResponse(
        body=FakeResponseBody(
            faked=Faked(string=req.body['string'], integer=req.body['integer'])
        ),
        headers=FakeHeaders(x_header=req.headers['x_header']),
    )


@pytest.fixture
def fake_app():
    return asgi_app([Route('/api/{id}', MethodType.GET, fake_controller)])


@pytest.fixture
def test_client(fake_app):
    return TestClient(fake_app)


@pytest.mark.asyncio
async def test_should_return_not_found(test_client):
    response = await test_client.get('/not-found')
    assert response.status_code == HTTPStatus.NOT_FOUND.value
    assert response.content == b''
    assert not response.headers


@pytest.mark.asyncio
async def test_should_return_method_not_allowed(test_client):
    response = await test_client.post('/api')
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED.value
    assert response.content == b''
    assert not response.headers


@pytest.mark.asyncio
async def test_should_return_bad_request_on_path_arg(test_client):
    response = await test_client.get('/api/invalid')
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'error': {
            'type': 'int',
            'field': 'id',
            'invalid_value': 'invalid',
            'name': 'ValueError',
            'cls': 'FakePathArgs',
        }
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_empty_query(test_client):
    response = await test_client.get('/api/1')
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'error': {
            'type': 'int',
            'field': 'query',
            'invalid_value': None,
            'cls': 'FakeQuery',
            'name': 'ParameterNotFoundError',
        }
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_invalid_type_query(test_client):
    response = await test_client.get('/api/1', params={'query': 'invalid'})
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'error': {
            'type': 'int',
            'field': 'query',
            'invalid_value': 'invalid',
            'name': 'ValueError',
            'cls': 'FakeQuery',
        }
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_empty_header(test_client):
    response = await test_client.get('/api/1', params={'query': '1'})
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'error': {
            'type': 'float',
            'field': 'x_header',
            'invalid_value': None,
            'cls': 'FakeHeaders',
            'name': 'ParameterNotFoundError',
        }
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_invalid_type_header(test_client):
    response = await test_client.get(
        '/api/1', params={'query': '1'}, headers={'x-header': 'invalid'}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'error': {
            'type': 'float',
            'field': 'x_header',
            'invalid_value': 'invalid',
            'name': 'ValueError',
            'cls': 'FakeHeaders',
        }
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_empty_body(test_client):
    response = await test_client.get(
        '/api/1', params={'query': '1'}, headers={'x-header': '0.1'}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'error': {
            'type': 'str',
            'field': 'string',
            'invalid_value': None,
            'name': 'ParameterNotFoundError',
            'cls': 'FakeBody',
        }
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_invalid_type_body(test_client):
    response = await test_client.get(
        '/api/1',
        params={'query': '1'},
        headers={'x-header': '0.1'},
        json={'string': 'str', 'integer': 'str'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'error': {
            'type': 'int',
            'field': 'integer',
            'invalid_value': 'str',
            'name': 'ValueError',
            'cls': 'FakeBody',
        }
    }


@pytest.mark.asyncio
async def test_should_return_ok(test_client):
    response = await test_client.get(
        '/api/1',
        params={'query': '1'},
        headers={'x-header': '0.1'},
        json={'integer': '1', 'string': 'apidaora'},
    )
    assert response.status_code == HTTPStatus.OK.value
    assert response.json() == {'faked': {'string': 'apidaora', 'integer': 1}}
    assert dict(response.headers) == {
        'x-header': '0.1',
        'Content-Type': 'application/json',
        'Content-Length': '43',
    }
