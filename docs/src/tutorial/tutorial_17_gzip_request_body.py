from apidaora import GZipFactory, appdaora, route


class GzipBody(GZipFactory):
    mode = 'rt'


@route.post('/hello')
def gzip_hello(body: GzipBody):
    with body.open() as file:
        return file.read()


app = appdaora(gzip_hello)
