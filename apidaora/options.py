from typing import Callable, List

from .header import Header
from .method import MethodType
from .responses import Response, no_content


class AllowHeader(Header, type=str, http_name='allow'):
    ...


def make_options_controller(
    methods: List[MethodType],
) -> Callable[[], Response]:
    def controller() -> Response:
        return no_content(
            headers=[AllowHeader(','.join([m.value for m in methods]))]
        )

    return controller
