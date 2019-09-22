from typing import Any, Dict, List, Optional, Tuple, TypedDict

from jsondaora import jsondaora

from ..content import ContentType


AsgiPathArgs = Dict[str, Any]
AsgiQueryDict = Dict[str, List[str]]
AsgiHeaders = List[Tuple[bytes, bytes]]


@jsondaora
class Headers(TypedDict):
    content_type: Optional[ContentType]
