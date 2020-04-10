import time

from apidaora import appdaora, route


@route.background('/hello')
def hello_task(name: str) -> str:
    time.sleep(1)
    return f'Hello {name}!'


app = appdaora(hello_task)
