from typing import TypedDict

from jsondaora import jsondaora, typed_dict_asjson

from apidaora.asgi.app import asgi_app
from apidaora.asgi.responses import JSON_RESPONSE
from apidaora.asgi.router import Route, make_router
from apidaora.method import MethodType


@jsondaora
class You(TypedDict):
    name: str
    location: str


async def hello_controller(path_args, query_dict, headers, body):
    you = You(name=path_args['name'], location=query_dict['location'][0])
    body = typed_dict_asjson(you, You)
    return JSON_RESPONSE, body


route = Route(
    path_pattern='/hello/{name}',
    method=MethodType.GET,
    controller=hello_controller,
    has_path_args=True,
    has_query=True,
)
router = make_router([route])
app = asgi_app(router)
