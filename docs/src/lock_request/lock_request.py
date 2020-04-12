from typing import List

from apidaora import LockRequestMiddleware, Middlewares, appdaora, route


prevent_request_middleware = LockRequestMiddleware()


@route.post(
    '/lock-request',
    middlewares=Middlewares(
        post_routing=[prevent_request_middleware.lock],
        pre_execution=[prevent_request_middleware.unlock_pre_execution],
    ),
)
async def lock_controller(body: List[int]) -> int:
    return len(body)


@route.post(
    '/lock-request-post',
    middlewares=Middlewares(
        post_routing=[prevent_request_middleware.lock],
        post_execution=[prevent_request_middleware.unlock_post_execution],
    ),
)
async def lock_post_controller(body: List[int]) -> int:
    return len(body)


app = appdaora([lock_controller, lock_post_controller])
