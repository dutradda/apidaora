from http import HTTPStatus
from typing import Any, Dict, Optional, Sequence

from dictdaora import DictDaora

from .content import ContentType
from .header import Header


class Response(DictDaora):
    status: HTTPStatus
    headers: Sequence[Header]
    content_type: Optional[ContentType]
    kwargs: Optional[Dict[str, Any]]


def json(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
    **kwargs: Any,
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.APPLICATION_JSON,
        kwargs=kwargs,
    )


def text(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
    **kwargs: Any,
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.TEXT_PLAIN,
        kwargs=kwargs,
    )


def html(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
    **kwargs: Any,
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.TEXT_HTML,
        kwargs=kwargs,
    )


def no_content(headers: Sequence[Header] = (), **kwargs: Any) -> Response:
    return Response(
        status=HTTPStatus.NO_CONTENT,
        headers=headers,
        content_type=None,
        body=None,
        kwargs=kwargs,
    )


def not_found(
    body: Optional[Any] = None,
    headers: Sequence[Header] = (),
    content_type: Optional[ContentType] = None,
    **kwargs: Any,
) -> Response:
    return Response(
        body=body,
        status=HTTPStatus.NOT_FOUND,
        headers=headers,
        content_type=content_type,
        kwargs=kwargs,
    )
