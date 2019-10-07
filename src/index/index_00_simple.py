from apidaora import appdaora, route


@route.get('/hello')
def hello_controller(name: str):
    return f'Hello {name}!'


app = appdaora(hello_controller)
