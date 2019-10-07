from dataclasses import dataclass
from typing import Any, Optional, Type


@dataclass
class Header:
    type: Type[Any]
    http_name: Optional[str] = None


def header(type: Type[Any], http_name: Optional[str] = None) -> Header:
    return Header(type, http_name)
