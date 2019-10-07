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
