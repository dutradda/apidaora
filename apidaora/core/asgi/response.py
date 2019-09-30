from typing import TypedDict, Tuple


class ASGIResponse(TypedDict):
    headers: Tuple[bytes, bytes]
    type: str = 'http.response.start'
    status: int = 200


JSON_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [
        [b'content-type', b'application/json'],
    ]
}

HTML_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [
        [b'content-type', b'text/html; charset=utf-8'],
    ]
}

PLAINTEXT_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [
        [b'content-type', b'text/plain; charset=utf-8'],
    ]
}

NOTFOUND_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 404,
    'headers': []
}

METHOD_NOT_ALLOWED_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 405,
    'headers': []
}

NO_CONTENT_RESPONSE: ASGIResponse = {
    'type': 'http.response.start',
    'status': 204,
    'headers': []
}


async def send_response(send, response, body):
    await send(response)
    await send({
        'type': 'http.response.body',
        'body': body,
        'more_body': False
    })


async def send_not_found(send):
    return send_response(send, NOTFOUND_RESPONSE, b'')


async def send_method_not_allowed_response(send):
    return send_response(send, METHOD_NOT_ALLOWED_RESPONSE, b'')
