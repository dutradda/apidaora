from apidaora import appdaora, gzip_body, route


@route.post('/hello')
def gzip_hello(body: gzip_body('rt')):
    with body.open() as file:
        return file.read()


app = appdaora(gzip_hello)
