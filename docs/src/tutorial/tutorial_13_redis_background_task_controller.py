import time

from apidaora import appdaora, route


@route.background('/hello', tasks_database='redis://')
def hello_task(name: str):
    time.sleep(1)
    return f'Hello {name}!'


app = appdaora(hello_task)
