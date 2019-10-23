from typing import Any, ClassVar, Optional, Type

from dictdaora import DictDaora
from jsondaora import as_typed_dict_field


BUILTIN_TYPE = type


class Header(DictDaora):
    type: ClassVar[Type[Any]]
    http_name: ClassVar[Optional[str]]

    def __init__(self, value: Any):
        value = as_typed_dict_field(value, 'value', type(self).type)
        super().__init__(value=value)

    def __init_subclass__(
        cls, type: Type[Any], http_name: Optional[str] = None
    ) -> None:
        cls.type = type
        cls.http_name = http_name
