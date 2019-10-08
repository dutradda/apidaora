from http import HTTPStatus
from typing import Any, Sequence

from dictdaora import DictDaora

from .content import ContentType
from .header import _Header


class Response(DictDaora):  # type: ignore
    status: HTTPStatus
    headers: Sequence[_Header]
    content_type: ContentType


def json(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[_Header] = (),
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
    headers: Sequence[_Header] = (),
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
    headers: Sequence[_Header] = (),
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.TEXT_HTML,
    )
