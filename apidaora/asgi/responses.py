from http import HTTPStatus
from typing import Awaitable, Optional, Tuple

from ..content import ContentType
from .base import ASGIHeaders, ASGIResponse, Sender


HTTP_RESPONSE_START = 'http.response.start'
JSON_CONTENT_HEADER = (
    b'content-type',
    ContentType.APPLICATION_JSON.value.encode(),
)
HTML_CONTENT_HEADER = (b'content-type', ContentType.TEXT_HTML.value.encode())
PLAINTEXT_CONTENT_HEADER = (
    b'content-type',
    ContentType.TEXT_PLAIN.value.encode(),
)

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
    'headers': (PLAINTEXT_CONTENT_HEADER,),
}

NOT_FOUND_RESPONSE: ASGIResponse = {
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


def make_response(
    content_length: Optional[int],
    status: HTTPStatus,
    headers: Optional[ASGIHeaders],
    default_value: ASGIResponse,
    default_content_header: Tuple[bytes, bytes],
) -> ASGIResponse:
    if content_length is None:
        return default_value

    default_headers: ASGIHeaders = (
        default_content_header,
        (b'content-length', str(content_length).encode()),
    )

    if headers:
        if isinstance(headers, tuple):
            headers = default_headers + headers
        else:
            headers = default_headers + tuple(headers)

    return {
        'type': HTTP_RESPONSE_START,
        'status': status.value,
        'headers': default_headers if not headers else headers,
    }


def make_json_response(
    content_length: Optional[int] = None,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Optional[ASGIHeaders] = None,
) -> ASGIResponse:
    return make_response(
        content_length, status, headers, JSON_RESPONSE, JSON_CONTENT_HEADER
    )


def make_text_response(
    content_length: Optional[int] = None,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Optional[ASGIHeaders] = None,
) -> ASGIResponse:
    return make_response(
        content_length,
        status,
        headers,
        PLAINTEXT_RESPONSE,
        PLAINTEXT_CONTENT_HEADER,
    )


def make_html_response(
    content_length: Optional[int] = None,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Optional[ASGIHeaders] = None,
) -> ASGIResponse:
    return make_response(
        content_length, status, headers, HTML_RESPONSE, HTML_CONTENT_HEADER
    )


async def send_response(
    send: Sender, response: ASGIResponse, body: bytes
) -> None:
    await send(response)  # type: ignore
    await send(
        {'type': 'http.response.body', 'body': body, 'more_body': False}
    )


def send_not_found(send: Sender) -> Awaitable[None]:
    return send_response(send, NOT_FOUND_RESPONSE, b'')


def send_method_not_allowed_response(send: Sender) -> Awaitable[None]:
    return send_response(send, METHOD_NOT_ALLOWED_RESPONSE, b'')
