from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Type


class ParameterType(Enum):
    HEADER = 'header'


@dataclass
class Parameter:
    annotation_name = None
    required = True


def header_param(schema: Type[Any], name: Optional[str] = None) -> Type[Any]:
    schema_ = schema
    name_ = name

    @dataclass
    class HeaderParameter(Parameter):
        name = name_
        schema = schema_
        in_ = ParameterType.HEADER

    return HeaderParameter
