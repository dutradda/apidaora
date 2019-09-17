# mypy: ignore-errors

from dataclasses import dataclass
from http import HTTPStatus

import pytest
from asgi_testclient import TestClient
from dataclassesjson import dataclassjson, integer, string

from dataclassesapi import App, MethodType, Route
from dataclassesapi.request import Body, Headers, PathArgs, Query, Request
from dataclassesapi.response import Body as ResponseBody
from dataclassesapi.response import Response


@dataclass
class FakePathArgs(PathArgs):
    id: int


@dataclass
class FakeQuery(Query):
    query: int


@dataclass
class FakeHeaders(Headers):
    x_header: float


@dataclass
class FakeBody(Body):
    string: str
    integer: int


@dataclass
class FakeRequest(Request):
    path_args: FakePathArgs
    query: FakeQuery
    headers: FakeHeaders
    body: FakeBody


@dataclass
class Faked:
    string: string(max_length=100)
    integer: integer(minimum=18)


@dataclass
class FakeResponseBody(ResponseBody):
    faked: Faked


@dataclassjson
@dataclass
class FakeResponse(Response):
    body: FakeResponseBody
    headers: FakeHeaders


def fake_controller(req: FakeRequest) -> FakeResponse:
    return FakeResponse(
        HTTPStatus.OK,
        body=FakeResponseBody(
            faked=Faked(string=req.body.string, integer=req.body.integer)
        ),
        headers=FakeHeaders(x_header=req.headers.x_header),
    )


@pytest.fixture
def fake_app():
    return App([Route('/api/{id}', MethodType.GET, fake_controller)])


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
        'type': 'int',
        'field': 'id',
        'invalid_value': 'invalid',
        'error': 'ValueError',
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_empty_query(test_client):
    response = await test_client.get('/api/1')
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'type': 'int',
        'field': 'query',
        'invalid_value': 'None',
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_invalid_type_query(test_client):
    response = await test_client.get('/api/1', params={'query': 'invalid'})
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'type': 'int',
        'field': 'query',
        'invalid_value': 'invalid',
        'error': 'ValueError',
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_empty_header(test_client):
    response = await test_client.get('/api/1', params={'query': '1'})
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'type': 'float',
        'field': 'x_header',
        'invalid_value': 'None',
    }


@pytest.mark.asyncio
async def test_should_return_bad_request_on_invalid_type_header(test_client):
    response = await test_client.get(
        '/api/1', params={'query': '1'}, headers={'x-header': 'invalid'}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert response.json() == {
        'type': 'float',
        'field': 'x_header',
        'invalid_value': 'invalid',
        'error': 'ValueError',
    }


@pytest.mark.asyncio
async def test_should_return_ok(test_client):
    response = await test_client.get(
        '/api/1',
        params={'query': '1'},
        headers={'x-header': '0.1'},
        json={'integer': '1', 'string': 'dataclassesapi'},
    )
    assert response.status_code == HTTPStatus.OK.value
    assert response.json() == {
        'faked': {'string': 'dataclassesapi', 'integer': 1}
    }
    assert dict(response.headers) == {
        'x-header': '0.1',
        'content-type': 'application/json',
        'content-length': '49',
    }
