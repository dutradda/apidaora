from http import HTTPStatus

import pytest
from asgi_testclient import TestClient
from jsondaora import jsondaora

from apidaora import MethodType, Response, appdaora, header_param, path


@pytest.fixture
def hello_fake():
    return 'Hello Fake!'


@jsondaora
class StrResponse(Response):
    body: str


@pytest.fixture
def simple_client(hello_fake):
    @path('/test/', MethodType.GET)
    def operation() -> StrResponse:
        return StrResponse(body=hello_fake)

    app = appdaora([operation])
    return TestClient(app)


@pytest.mark.asyncio
async def test_should_get_response_without_arguments(
    simple_client, hello_fake
):
    response = await simple_client.get('/test/')

    assert response.status_code == HTTPStatus.OK.value
    assert response.content == hello_fake.encode()


@pytest.mark.asyncio
async def test_should_get_response_without_arguments_and_slash(
    simple_client, hello_fake
):
    response = await simple_client.get('/test')

    assert response.status_code == HTTPStatus.OK.value
    assert response.content == hello_fake.encode()


@pytest.mark.asyncio
async def test_should_get_response_with_one_scalar_path_parameter():
    @path('/test/{param}', MethodType.GET)
    def operation(param: int) -> StrResponse:
        return StrResponse(body=f'{param}: {type(param).__name__}')

    client = TestClient(appdaora([operation]))

    response = await client.get('/test/01')

    assert response.status_code == HTTPStatus.OK.value
    assert response.content == b'1: int'


@pytest.mark.asyncio
async def test_should_get_response_with_two_scalar_path_parameters():
    @path('/test/{param}/{param2}', MethodType.GET)
    def operation(param: int, param2: float) -> StrResponse:
        return StrResponse(
            body=f'{param}: {type(param).__name__}, {param2}: {type(param2).__name__}'
        )

    client = TestClient(appdaora([operation]))

    response = await client.get('/test/01/00000.1')

    assert response.status_code == HTTPStatus.OK.value
    assert response.content == b'1: int, 0.1: float'


@pytest.mark.asyncio
async def test_should_get_response_with_one_scalar_path_parameter_and_one_query_parameter():
    @path('/test/{param}', MethodType.GET)
    def operation(param: int, param2: float) -> StrResponse:
        return StrResponse(
            body=f'{param}: {type(param).__name__}, {param2}: {type(param2).__name__}'
        )

    client = TestClient(appdaora([operation]))

    response = await client.get('/test/01/?param2=00000.1')

    assert response.status_code == HTTPStatus.OK.value
    assert response.content == b'1: int, 0.1: float'


@pytest.mark.asyncio
async def test_should_get_response_with_one_scalar_path_parameter_and_two_query_parameter():
    @path('/test/{param}', MethodType.GET)
    def operation(param: int, param2: float, param3: str) -> StrResponse:
        return StrResponse(
            body=(
                f'{param}: {type(param).__name__}, '
                f'{param2}: {type(param2).__name__}, '
                f'{param3}: {type(param3).__name__}'
            )
        )

    client = TestClient(appdaora([operation]))

    response = await client.get('/test/01/?param2=00000.1&param3=test')

    assert response.status_code == HTTPStatus.OK.value
    assert response.content == b'1: int, 0.1: float, test: str'


@pytest.mark.asyncio
async def test_should_get_response_with_scalar_parameters_with_one_path_and_one_query_and_one_header():
    @path('/test/{param}', MethodType.GET)
    def operation(
        param: int,
        param2: float,
        param3: header_param(schema=float, name='x-param3'),
    ) -> StrResponse:
        return StrResponse(
            body=(
                f'{param}: {type(param).__name__}, '
                f'{param2}: {type(param2).__name__}, '
                f'{param3}: {type(param3).__name__}'
            )
        )

    client = TestClient(appdaora([operation]))

    response = await client.get(
        '/test/01/?param2=00000.1', headers={'x-param3': '-000.1'}
    )

    assert response.status_code == HTTPStatus.OK.value
    assert response.content == b'1: int, 0.1: float, -0.1: float'
