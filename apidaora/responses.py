from http import HTTPStatus
from typing import Any, Optional, Sequence

from dictdaora import DictDaora

from .content import ContentType
from .header import Header


class Response(DictDaora):
    status: HTTPStatus
    headers: Sequence[Header]
    content_type: Optional[ContentType]


def json(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.APPLICATION_JSON,
    )


def text(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.TEXT_PLAIN,
    )


def html(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.TEXT_HTML,
    )


def no_content(headers: Sequence[Header] = ()) -> Response:
    return Response(
        status=HTTPStatus.NO_CONTENT,
        headers=headers,
        content_type=None,
        body=None,
    )


def not_found(
    body: Optional[Any] = None,
    headers: Sequence[Header] = (),
    content_type: Optional[ContentType] = None,
) -> Response:
    return Response(
        body=body,
        status=HTTPStatus.NOT_FOUND,
        headers=headers,
        content_type=content_type,
    )
