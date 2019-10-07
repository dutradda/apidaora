from typing import Any, ClassVar, Optional, Type

from dictdaora import DictDaora
from jsondaora import as_typed_dict_field


BUILTIN_TYPE = type


class _Header(DictDaora):  # type: ignore
    def __init__(self, value: Any):
        value = as_typed_dict_field(value, 'value', type(self).type)
        super().__init__(value=value)


def header(
    type: Type[Any], http_name: Optional[str] = None
) -> Type[DictDaora]:
    annotations = {
        'type': ClassVar[Type[Any]],
        'http_name': ClassVar[Optional[str]],
        'value': Any,
    }
    return BUILTIN_TYPE(
        'Header',
        (_Header,),
        {'__annotations__': annotations, 'http_name': http_name, 'type': type},
    )
