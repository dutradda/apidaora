from typing import TypedDict

from jsondaora import jsondaora, typed_dict_asjson

from apidaora.core import appdaora_core, route
from apidaora.core.responses import JSON_RESPONSE


@jsondaora
class You(TypedDict):
    name: str
    location: str


@route.get('/hello/{name}', query=True)
async def hello_controller(path_args, query_dict, headers, body):
    you = You(name=path_args['name'], location=query_dict['location'][0])
    body = typed_dict_asjson(you, You)
    return JSON_RESPONSE, body


app = appdaora_core(hello_controller)
