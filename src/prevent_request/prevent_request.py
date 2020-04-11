from typing import List

from apidaora import Middlewares, PreventRequestMiddleware, appdaora, route


prevent_request_middleware = PreventRequestMiddleware()


@route.post(
    '/prevent-request',
    middlewares=Middlewares(
        post_routing=[prevent_request_middleware.set_in_process],
        pre_execution=[prevent_request_middleware.remove_in_process],
    ),
)
async def pre_execution_middleware_controller(body: List[int]) -> int:
    return len(body)


app = appdaora(pre_execution_middleware_controller)
