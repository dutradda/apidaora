from apidaora import ClassController, appdaora


class HelloWorld(ClassController, path='/hello'):
    def get(self) -> str:
        return 'Hello World!'

    def post(self, body: str) -> str:
        return f'Hello {body}!'


class HelloDuckType:
    path = '/hello-duck'

    def get(self) -> str:
        return 'Hello Duck!'


app = appdaora([HelloWorld, HelloDuckType])
