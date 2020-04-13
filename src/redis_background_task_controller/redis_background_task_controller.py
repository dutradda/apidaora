import os
import time

from apidaora import appdaora, route


REDIS_URI = f"redis://{os.environ.get('REDIS', '')}"


@route.background('/hello', tasks_repository_uri=REDIS_URI)
def hello_task(name: str) -> str:
    time.sleep(1)
    return f'Hello {name}!'


app = appdaora(hello_task)
