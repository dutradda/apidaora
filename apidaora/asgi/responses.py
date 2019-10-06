from http import HTTPStatus
from typing import Awaitable, Optional

from .base import ASGIResponse, Sender


HTTP_RESPONSE_START = 'http.response.start'
JSON_CONTENT_HEADER = (b'content-type', b'application/json')
HTML_CONTENT_HEADER = (b'content-type', b'text/html; charset=utf-8')
TEXT_CONTENT_HEADER = (b'content-type', b'text/plain; charset=utf-8')

JSON_RESPONSE: ASGIResponse = {
    'type': HTTP_RESPONSE_START,
    'status': HTTPStatus.OK.value,
    'headers': (JSON_CONTENT_HEADER,),
}

HTML_RESPONSE: ASGIResponse = {
    'type': HTTP_RESPONSE_START,
    'status': HTTPStatus.OK.value,
    'headers': (HTML_CONTENT_HEADER,),
}

PLAINTEXT_RESPONSE: ASGIResponse = {
    'type': HTTP_RESPONSE_START,
    'status': HTTPStatus.OK.value,
    'headers': (TEXT_CONTENT_HEADER,),
}

NOTFOUND_RESPONSE: ASGIResponse = {
    'type': HTTP_RESPONSE_START,
    'status': HTTPStatus.NOT_FOUND.value,
    'headers': (),
}

METHOD_NOT_ALLOWED_RESPONSE: ASGIResponse = {
    'type': HTTP_RESPONSE_START,
    'status': HTTPStatus.METHOD_NOT_ALLOWED.value,
    'headers': (),
}

NO_CONTENT_RESPONSE: ASGIResponse = {
    'type': HTTP_RESPONSE_START,
    'status': HTTPStatus.NO_CONTENT.value,
    'headers': (),
}


def make_json_response(
    content_length: Optional[int] = None, status: HTTPStatus = HTTPStatus.OK
) -> ASGIResponse:
    if content_length is None:
        return JSON_RESPONSE

    return {
        'type': HTTP_RESPONSE_START,
        'status': status.value,
        'headers': (
            JSON_CONTENT_HEADER,
            (b'content-length', str(content_length).encode()),
        ),
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
