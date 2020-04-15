from apidaora import (
    BackgroundTaskMiddleware,
    Middlewares,
    Response,
    appdaora,
    route,
    text,
)


class HelloCounter:
    counter = 1

    @classmethod
    def count(cls) -> None:
        cls.counter += 1


@route.get('/background-tasks')
async def background_tasks_controller(name: str) -> Response:
    return text(
        f'Hello {name}!\n{name} are the #{HelloCounter.counter}!',
        background_tasks=HelloCounter.count,
    )


app = appdaora(
    background_tasks_controller,
    middlewares=Middlewares(post_execution=BackgroundTaskMiddleware()),
)
