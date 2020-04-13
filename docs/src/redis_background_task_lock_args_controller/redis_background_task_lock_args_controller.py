import asyncio
import os

from apidaora import appdaora, route


REDIS_URI = f"redis://{os.environ.get('REDIS', '')}"


@route.background(
    '/hello-single', lock_args=True, tasks_repository_uri=REDIS_URI
)
async def hello_task(name: str) -> str:
    await asyncio.sleep(1)
    return f'Hello {name}!'


app = appdaora(hello_task)
