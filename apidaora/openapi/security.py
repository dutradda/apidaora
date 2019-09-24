from enum import Enum
from typing import TypedDict

from jsondaora import jsondaora


@jsondaora
class Security(TypedDict):
    ...


class SecurityType(Enum):
    OAUTH2 = 'OAuth2'
