from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class AsgiRequest:
    path_pattern: str
    resolved_path: str
    path_args: Dict[str, Any]
    query_dict: Dict[str, Any]
    headers: List[Tuple[bytes, bytes]]
    body: bytes
