from typing import Any, Dict, List, Tuple, TypedDict

from jsondaora import jsondaora


AsgiPathArgs = Dict[str, Any]
AsgiQueryDict = Dict[str, List[str]]
AsgiHeaders = List[Tuple[bytes, bytes]]


@jsondaora
class Headers(TypedDict):
    ...
