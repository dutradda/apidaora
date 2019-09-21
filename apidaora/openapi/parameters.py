from typing import Literal, TypedDict

from jsondaora import jsondaora


@jsondaora
class PathParameter(TypedDict):
    required: Literal[True]
    in_: Literal['path']
