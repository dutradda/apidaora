from typing import TypedDict

from jsondaora import jsondaora, typed_dict_asjson

from apidaora.core import JSON_RESPONSE, appdaora_core, route


@jsondaora
class You(TypedDict):
    name: str
    location: str


@route.get('/hello/{name}', query=True)
async def hello_controller(request):  # type: ignore
    you = You(
        name=request.path_args['name'],
        location=request.query_dict['location'][0],
    )
    body = typed_dict_asjson(you, You)
    return JSON_RESPONSE, body


app = appdaora_core(hello_controller)
