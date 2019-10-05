import functools
from typing import Any, Callable, Dict, Iterable, Type, TypedDict

from jsondaora import as_typed_dict, jsondaora

from dictdaora import DictDaora

from ..core.asgi.base import (
    ASGIBody,
    ASGICallable,
    ASGICallableResults,
    ASGIHeaders,
    ASGIPathArgs,
    ASGIQueryDict,
)


def operation(handler: Callable[[...], Any]) -> ASGICallable:
    has_input = False
    has_path_args = False
    has_query_dict = False
    has_headers = False
    has_body = False

    if hasattr(handler, '__annotations__'):
        annotations_path_args = get_annotations_path_args(
            handler.__annotations__
        )
        annotations_query_dict = get_annotations_query_dict(
            handler.__annotations__
        )
        annotations_headers = get_annotations_headers(handler.__annotations__)
        annotations_body = get_annotations_body(handler.__annotations__)
        all_annotations = (
            annotations_path_args,
            annotations_query_dict,
            annotations_headers,
            annotations_body,
        )
        annotations = {
            name: type_
            for partial_annotations in all_annotations
            for name, type_ in partial_annotations.items()
        }

        if annotations:
            has_input = True

            if annotations_path_args:
                has_path_args = True

            if annotations_query_dict:
                has_query_dict = True

            if annotations_headers:
                has_headers = True

            if annotations_body:
                has_body = True
                body_name = annotations_body.keys()[-1]

            OperationInput = jsondaora(
                type(
                    'OperationInput',
                    (DictDaora,),
                    {'__annotations__': annotations},
                )
            )

    def parse_asgi_input(
        path_args: ASGIPathArgs,
        query_dict: ASGIQueryDict,
        headers: ASGIHeaders,
        body: ASGIBody,
    ) -> Dict[str, Any]:
        if has_input:
            if has_path_args:
                kwargs = {
                    name: path_args.get(name)
                    for name in annotations_path_args.keys()
                }
            else:
                kwargs = {}

            if has_query_dict:
                kwargs.update(
                    {
                        name: query_dict.get(name)
                        for name in annotations_query_dict.keys()
                    }
                )

            if has_headers:
                kwargs.update(
                    {
                        name: h_value.decode()
                        for h_name, h_value in headers
                        if (name := h_name.decode()) in annotations_headers
                    }
                )

            if has_body:
                kwargs[body_name] = body

            return as_typed_dict(kwargs, OperationInput)

        return {}

    def build_asgi_output(handler_output: Any) -> ASGICallableResults:
        ...

    @functools.wraps(handler)
    def wrapper(
        path_args: ASGIPathArgs,
        query_dict: ASGIQueryDict,
        headers: ASGIHeaders,
        body: ASGIBody,
    ) -> ASGICallableResults:
        kwargs = parse_asgi_input(path_args, query_dict, headers, body)
        handler_output = handler(**kwargs)
        return build_asgi_output(handler_output)

    wrapper.__has_path_args__ = has_path_args
    wrapper.__has_query_dict__ = has_query_dict
    wrapper.__has_headers__ = has_headers
    wrapper.__body__ = has_body
    return wrapper


def get_annotations_path_args(
    annotations: Dict[str, Type[Any]]
) -> Dict[str, Type[Any]]:
    ...


def get_annotations_query_dict(
    annotations: Dict[str, Type[Any]]
) -> Dict[str, Type[Any]]:
    ...


def get_annotations_headers(
    annotations: Dict[str, Type[Any]]
) -> Dict[str, Type[Any]]:
    ...


def get_annotations_body(
    annotations: Dict[str, Type[Any]]
) -> Dict[str, Type[Any]]:
    ...
