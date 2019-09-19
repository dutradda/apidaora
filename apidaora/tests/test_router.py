# mypy: ignore-errors

import pytest

from apidaora.exceptions import MethodNotFoundError, PathNotFoundError
from apidaora.method import MethodType
from apidaora.router import Route, route
from apidaora.router import router as http_router


class TestRouter:
    @pytest.fixture
    def method(self):
        return MethodType.GET

    @pytest.fixture
    def controller(self):
        return lambda: None

    @pytest.fixture
    def controller2(self):
        return lambda: None

    @pytest.fixture
    def controller3(self):
        return lambda: None

    def test_should_route_path_without_slash(self, method, controller):
        path = '/dataclasses'
        router = http_router([Route(path, method, controller)])

        resolved = route(router, path, method.value)

        assert resolved.route.caller is controller

    def test_should_route_path_with_slash(self, method, controller):
        path = '/dataclasses/api'
        router = http_router([Route(path, method, controller)])

        resolved = route(router, path, method.value)

        assert resolved.route.caller is controller

    def test_should_route_path_with_path_arg_name(self, method, controller):
        path_pattern = r'/{id}'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/012'

        resolved = route(router, path, method.value)

        assert resolved.route.caller is controller
        assert resolved.path_args == {'id': '012'}

    def test_should_route_path_with_regex(self, method, controller):
        path_pattern = r'/{id:\d{3}}'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/012'

        resolved = route(router, path, method.value)

        assert resolved.route.caller is controller
        assert resolved.path_args == {'id': '012'}

    def test_should_route_path_with_slash_and_regex(self, method, controller):
        path_pattern = r'/api/{id:\d{3}}'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/api/012'

        resolved = route(router, path, method.value)

        assert resolved.route.caller is controller
        assert resolved.path_args == {'id': '012'}

    def test_should_route_path_with_regex_and_slash(self, method, controller):
        path_pattern = r'/{id:\d{3}}/apidaora'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/012/apidaora'

        resolved = route(router, path, method.value)

        assert resolved.route.caller is controller

    def test_should_not_route_path_without_slash(self, method, controller):
        path_pattern = '/api'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/invalid'

        with pytest.raises(PathNotFoundError) as exc_info:
            route(router, path, method)

        assert exc_info.value.args == (path,)

    def test_should_not_route_path_with_slash(self, method, controller):
        path_pattern = '/api/apidaora'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/api/invalid'

        with pytest.raises(PathNotFoundError) as exc_info:
            route(router, path, method.value)

        assert exc_info.value.args == (path,)

    def test_should_not_route_path_with_regex(self, method, controller):
        path_pattern = r'/{id:\d{3}}'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/0'

        with pytest.raises(PathNotFoundError) as exc_info:
            route(router, path, method.value)

        assert exc_info.value.args == (path,)

    def test_should_not_route_path_with_slash_and_regex(
        self, method, controller
    ):
        path_pattern = r'/api/{id:\d{3}}'
        router = http_router([Route(path_pattern, method, controller)])
        path = '/api/0'

        with pytest.raises(PathNotFoundError) as exc_info:
            route(router, path, method.value)

        assert exc_info.value.args == (path,)

    def test_should_not_route_method(self, method, controller):
        path = '/api'
        router = http_router([Route(path, method, controller)])

        with pytest.raises(MethodNotFoundError) as exc_info:
            route(router, path, MethodType.POST.value)

        assert exc_info.value.args == (MethodType.POST.value, path)

    def test_should_route_three_paths_with_common_parts(
        self, method, controller, controller2, controller3
    ):
        path1_pattern = r'/apis/dataclasses/{id:\d{3}}'
        path2_pattern = r'/apis/dataclasses/{id:\d{3}}/{type}'
        # path3_pattern = r'/apis/dataclasses/{id:\d{3}}/{type}/{value:.+}'

        router = http_router(
            [
                Route(path1_pattern, method, controller),
                Route(path2_pattern, method, controller2),
                # Route(path3_pattern, method, controller3),
            ]
        )

        path1 = '/apis/dataclasses/012'
        path2 = '/apis/dataclasses/013/apis'
        # path3 = '/apis/dataclasses/014/api/dataclasses'

        resolved1 = route(router, path1, method.value)
        resolved2 = route(router, path2, method.value)
        # resolved3 = route(router, path3, method.value)

        assert resolved1.route.caller is controller
        assert resolved2.route.caller is controller2
        # assert resolved3.route.caller is controller3

        assert resolved1.path_args == {'id': '012'}
        assert resolved2.path_args == {'id': '013', 'type': 'apis'}
        # assert resolved3.path_args == {
        #     'id': '014',
        #     'type': 'api',
        #     'value': 'dataclasses',
        # }
