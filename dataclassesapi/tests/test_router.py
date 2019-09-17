# mypy: ignore-errors

import pytest

from dataclassesapi.exceptions import MethodNotFoundError, PathNotFoundError
from dataclassesapi.method import MethodType
from dataclassesapi.router import Route, Router


class TestRouter:
    @pytest.fixture
    def router(self):
        return Router()

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

    def test_should_route_path_without_slash(self, router, method, controller):
        path = '/dataclasses'
        router.add_routes([Route(path, method, controller)])

        resolved = router.route(path, method.value)

        assert resolved.route.caller is controller

    def test_should_route_path_with_slash(self, router, method, controller):
        path = '/dataclasses/api'
        router.add_routes([Route(path, method, controller)])

        resolved = router.route(path, method.value)

        assert resolved.route.caller is controller

    def test_should_route_path_with_path_arg_name(
        self, router, method, controller
    ):
        path_pattern = r'/{id}'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/012'

        resolved = router.route(path, method.value)

        assert resolved.route.caller is controller
        assert resolved.path_args == {'id': '012'}

    def test_should_route_path_with_regex(self, router, method, controller):
        path_pattern = r'/{id:\d{3}}'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/012'

        resolved = router.route(path, method.value)

        assert resolved.route.caller is controller
        assert resolved.path_args == {'id': '012'}

    def test_should_route_path_with_slash_and_regex(
        self, router, method, controller
    ):
        path_pattern = r'/api/{id:\d{3}}'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/api/012'

        resolved = router.route(path, method.value)

        assert resolved.route.caller is controller
        assert resolved.path_args == {'id': '012'}

    def test_should_route_path_with_regex_and_slash(
        self, router, method, controller
    ):
        path_pattern = r'/{id:\d{3}}/dataclassesapi'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/012/dataclassesapi'

        resolved = router.route(path, method.value)

        assert resolved.route.caller is controller

    def test_should_not_route_path_without_slash(
        self, router, method, controller
    ):
        path_pattern = '/api'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/invalid'

        with pytest.raises(PathNotFoundError) as exc_info:
            router.route(path, method)

        assert exc_info.value.args == (path,)

    def test_should_not_route_path_with_slash(
        self, router, method, controller
    ):
        path_pattern = '/api/dataclassesapi'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/api/invalid'

        with pytest.raises(PathNotFoundError) as exc_info:
            router.route(path, method.value)

        assert exc_info.value.args == (path,)

    def test_should_not_route_path_with_regex(
        self, router, method, controller
    ):
        path_pattern = r'/{id:\d{3}}'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/0'

        with pytest.raises(PathNotFoundError) as exc_info:
            router.route(path, method.value)

        assert exc_info.value.args == (path,)

    def test_should_not_route_path_with_slash_and_regex(
        self, router, method, controller
    ):
        path_pattern = r'/api/{id:\d{3}}'
        router.add_routes([Route(path_pattern, method, controller)])
        path = '/api/0'

        with pytest.raises(PathNotFoundError) as exc_info:
            router.route(path, method.value)

        assert exc_info.value.args == (path,)

    def test_should_not_route_method(self, router, method, controller):
        path = '/api'
        router.add_routes([Route(path, method, controller)])

        with pytest.raises(MethodNotFoundError) as exc_info:
            router.route(path, MethodType.POST.value)

        assert exc_info.value.args == (path, MethodType.POST.value)

    def test_should_route_three_paths_with_common_parts(
        self, router, method, controller, controller2, controller3
    ):
        path1_pattern = r'/apis/dataclasses/{id:\d{3}}'
        path2_pattern = r'/apis/dataclasses/{id:\d{3}}/{type}'
        path3_pattern = r'/apis/dataclasses/{id:\d{3}}/{type}/{value:.+}'

        router.add_routes([Route(path1_pattern, method, controller)])
        router.add_routes([Route(path2_pattern, method, controller2)])
        router.add_routes([Route(path3_pattern, method, controller3)])

        path1 = '/apis/dataclasses/012'
        path2 = '/apis/dataclasses/013/apis'
        path3 = '/apis/dataclasses/014/api/dataclasses'

        resolved1 = router.route(path1, method.value)
        resolved2 = router.route(path2, method.value)
        resolved3 = router.route(path3, method.value)

        assert resolved1.route.caller is controller
        assert resolved2.route.caller is controller2
        assert resolved3.route.caller is controller3

        assert resolved1.path_args == {'id': '012'}
        assert resolved2.path_args == {'id': '013', 'type': 'apis'}
        assert resolved3.path_args == {
            'id': '014',
            'type': 'api',
            'value': 'dataclasses',
        }
