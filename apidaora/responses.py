from http import HTTPStatus
from typing import Any, Dict, Optional, Sequence

from dictdaora import DictDaora

from .content import ContentType
from .header import Header


class Response(DictDaora):
    status: HTTPStatus
    headers: Sequence[Header]
    content_type: Optional[ContentType]
    ctx: Optional[Dict[str, Any]]


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
        ctx=kwargs,
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
        ctx=kwargs,
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
        ctx=kwargs,
    )


def no_content(headers: Sequence[Header] = (), **kwargs: Any) -> Response:
    return Response(
        status=HTTPStatus.NO_CONTENT,
        headers=headers,
        content_type=None,
        body=None,
        ctx=kwargs,
    )


def see_other(headers: Sequence[Header] = (), **kwargs: Any) -> Response:
    return Response(
        status=HTTPStatus.SEE_OTHER,
        headers=headers,
        content_type=None,
        body=None,
        ctx=kwargs,
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
        ctx=kwargs,
    )


def css(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
    **kwargs: Any,
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.TEXT_CSS,
        ctx=kwargs,
    )


def javascript(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Sequence[Header] = (),
    **kwargs: Any,
) -> Response:
    return Response(
        body=body,
        status=status,
        headers=headers,
        content_type=ContentType.TEXT_JAVASCRIPT,
        ctx=kwargs,
    )
