from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, Type

from dictdaora import DictDaora
from jsondaora import jsondaora

from .annotations_getters import (
    get_annotations_body,
    get_annotations_headers,
    get_annotations_path_args,
    get_annotations_query_dict,
)


@dataclass
class AnnotationsInfo:
    has_input: bool = False
    has_path_args: bool = False
    has_query_dict: bool = False
    has_headers: bool = False
    has_body: bool = False


class ControllerInput(DictDaora):  # type: ignore
    __annotations_info__: ClassVar[AnnotationsInfo]
    __annotations_path_args__: ClassVar[Dict[str, Type[Any]]]
    __annotations_query_dict__: ClassVar[Dict[str, Type[Any]]]
    __annotations_headers__: ClassVar[Dict[str, Type[Any]]]
    __annotations_body__: ClassVar[Dict[str, Type[Any]]]
    __headers_name_map__: ClassVar[Dict[str, str]]


def controller_input(
    controller: Callable[..., Any], path_pattern: str
) -> Type[ControllerInput]:
    annotations_info = AnnotationsInfo()
    headers_name_map: Dict[str, str] = {}

    if hasattr(controller, '__annotations__'):
        annotations_path_args = get_annotations_path_args(
            path_pattern, controller.__annotations__
        )
        annotations_headers = get_annotations_headers(
            headers_name_map, controller.__annotations__
        )
        annotations_query_dict = get_annotations_query_dict(
            annotations_path_args,
            annotations_headers,
            controller.__annotations__,
        )
        annotations_body = get_annotations_body(controller.__annotations__)
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
            annotations_info.has_input = True

            if annotations_path_args:
                annotations_info.has_path_args = True

            if annotations_query_dict:
                annotations_info.has_query_dict = True

            if annotations_headers:
                annotations_info.has_headers = True

            if annotations_body:
                annotations_info.has_body = True

            AnnotatedControllerInput = jsondaora(
                type(
                    'AnnotatedControllerInput',
                    (ControllerInput,),
                    {
                        '__annotations__': annotations,
                        '__annotations_info__': annotations_info,
                        '__annotations_path_args__': annotations_path_args,
                        '__annotations_query_dict__': annotations_query_dict,
                        '__annotations_headers__': annotations_headers,
                        '__annotations_body__': annotations_body,
                        '__headers_name_map__': headers_name_map,
                    },
                )
            )
            return AnnotatedControllerInput  # type: ignore

    return ControllerInput
