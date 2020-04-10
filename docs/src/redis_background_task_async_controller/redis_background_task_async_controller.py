import asyncio
import os

from apidaora import appdaora, route


REDIS_URI = f"redis://{os.environ.get('REDIS', '')}"


@route.background('/hello', tasks_repository=REDIS_URI)
async def hello_task(name: str):
    await asyncio.sleep(1)
    return f'Hello {name}!'


app = appdaora(hello_task)
