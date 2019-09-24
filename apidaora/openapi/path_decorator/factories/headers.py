from logging import getLogger
from typing import (  # type: ignore
    Any,
    Dict,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    _GenericAlias,
    _TypedDictMeta,
)

from jsondaora import jsondaora

from ....core.headers import Headers
from ...parameters import Parameter, ParameterType


logger = getLogger(__name__)


def request_headers(
    operation_annotations: Dict[str, Any], headers_names: Dict[str, str]
) -> Type[Headers]:
    headers_fields = set()
    optional_fields: Set[Tuple[str, Type[Any]]] = set()
    annotations: Dict[str, Any] = {}
    attrs: Dict[str, Any] = {}

    for param_name, param_type in operation_annotations.items():
        if (
            isinstance(param_type, type)
            and issubclass(param_type, Parameter)
            and param_type.in_ is ParameterType.HEADER
        ):
            parse_header_param(
                param_type,
                param_name,
                headers_names,
                optional_fields,
                headers_fields,
            )

    for k, v in headers_fields:
        if (k, v) in optional_fields:
            v = Optional[v]
            attrs[k] = None

        annotations[k] = v

    attrs['__annotations__'] = annotations
    request_headers_type = _TypedDictMeta('OperationHeaders', (), attrs)
    request_headers_type: Type[Headers] = jsondaora(request_headers_type)
    return request_headers_type


def parse_header_param(
    param_type,
    operation_param_name,
    headers_names,
    optional_fields,
    headers_fields,
) -> None:
    param_type_name = (
        param_type.name.replace('-', '_') if param_type.name else None
    )
    field_name = param_type_name or operation_param_name

    if param_type_name:
        headers_names[param_type_name] = operation_param_name

    field_type = get_field_type(param_type)
    field = (field_name, field_type)

    if not param_type.required:
        optional_fields.add(field)

    headers_fields.add(field)


def get_field_type(param_type):
    field_type = param_type.schema

    if (
        isinstance(field_type, _GenericAlias)
        and field_type.__origin__ is Union
    ):
        field_types = set()

        for union_type in field_type.__args__:
            if union_type is type(None) or union_type is None:  # noqa
                param_type.required = False

            elif (
                issubclass(param_type, Parameter)
                and param_type.in_ is ParameterType.HEADER
            ):
                field_types.add(union_type)

        union_types = [f_type.__name__ for f_type in field_types]

        if not param_type.required:
            union_types.append('None')

        field_type = Union[eval(', '.join(union_types))]

    return field_type
