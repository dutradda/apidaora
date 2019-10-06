from typing import Any, Dict, Type

from ..header import Header


def get_annotations_path_args(
    path_pattern: str, annotations: Dict[str, Type[Any]]
) -> Dict[str, Type[Any]]:
    return {
        name: type_
        for name, type_ in annotations.items()
        if f'{{{name}}}' in path_pattern
    }


def get_annotations_query_dict(
    path_args_annotations: Dict[str, Type[Any]],
    headers_annotations: Dict[str, Type[Any]],
    annotations: Dict[str, Type[Any]],
) -> Dict[str, Type[Any]]:
    return {
        name: type_
        for name, type_ in annotations.items()
        if name not in path_args_annotations
        and name not in headers_annotations
        and name != 'return'
    }


def get_annotations_headers(
    headers_name_map: Dict[str, str], annotations: Dict[str, Type[Any]]
) -> Dict[str, Type[Any]]:
    annotations_headers: Dict[str, Type[Header]] = {}

    for name, type_ in annotations.items():
        if isinstance(type_, Header):
            if type_.http_name is None:
                http_name = (
                    ''
                    if name.startswith('x-') or name.startswith('x_')
                    else 'x-'
                )
                http_name += name.replace('_', '-')
                type_.http_name = http_name
            else:
                http_name = type_.http_name

            annotations_headers[name] = type_.type
            headers_name_map[http_name] = name

    return annotations_headers


def get_annotations_body(
    annotations: Dict[str, Type[Any]]
) -> Dict[str, Type[Any]]:
    body_type = annotations.get('body')

    if body_type:
        return {'body': body_type}

    return {}
