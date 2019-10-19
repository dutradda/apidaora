import asyncio

from apidaora import appdaora, route


# async tasks can potentially block yours event loop, use with care
# it use is recommended just for small tasks and non-blocking operations
@route.background('/hello')
async def hello_task(name: str):
    await asyncio.sleep(1)
    return f'Hello {name}!'


app = appdaora(hello_task)
