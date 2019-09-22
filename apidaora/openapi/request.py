from typing import Any, Dict

from jsondaora import jsondaora

from ..content import ContentType


@jsondaora
class JSONRequestBody:
    content: Dict[str, Any]


JSONRequestBody.__content_type__: ContentType = ContentType.APPLICATION_JSON  # type: ignore
