from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Type


class ParameterType(Enum):
    HEADER = 'header'


@dataclass
class Parameter:
    in_: ParameterType
    name: Optional[str]
    schema: Type[Any]
    required: bool = True
    description: str = ''


def header_param(schema: Type[Any], name: Optional[str] = None) -> Type[Any]:
    schema_ = schema
    name_ = name

    @dataclass
    class HeaderParameter(Parameter):
        ...

    HeaderParameter.name = name_
    HeaderParameter.schema = schema_
    HeaderParameter.in_ = ParameterType.HEADER

    return HeaderParameter
