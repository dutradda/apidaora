import asyncio

from apidaora import appdaora, route


# async tasks can potentially block yours application, use with care
# it use is recommended just for small tasks or non-blocking operations
@route.background('/hello')
async def hello_task(name: str):
    await asyncio.sleep(1)
    return f'Hello {name}!'


app = appdaora(hello_task)
