from typing import Awaitable, List, Tuple, TypedDict

from .base import Sender


class ASGIResponse(TypedDict):
    headers: List[Tuple[bytes, bytes]]
    type: str
    status: int


JSON_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [(b'content-type', b'application/json')],
}

HTML_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [(b'content-type', b'text/html; charset=utf-8')],
}

PLAINTEXT_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [(b'content-type', b'text/plain; charset=utf-8')],
}

NOTFOUND_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 404,
    'headers': [],
}

METHOD_NOT_ALLOWED_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 405,
    'headers': [],
}

NO_CONTENT_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 204,
    'headers': [],
}


async def send_response(
    send: Sender, response: ASGIResponse, body: bytes
) -> None:
    await send(response)  # type: ignore
    await send(
        {'type': 'http.response.body', 'body': body, 'more_body': False}
    )


def send_not_found(send: Sender) -> Awaitable[None]:
    return send_response(send, NOTFOUND_RESPONSE, b'')


def send_method_not_allowed_response(send: Sender) -> Awaitable[None]:
    return send_response(send, METHOD_NOT_ALLOWED_RESPONSE, b'')
