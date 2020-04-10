from apidaora import appdaora, route


@route.get('/app-options')
async def app_options() -> str:
    return 'Options'


@route.get('/route-options', options=True)
async def route_options() -> str:
    return 'Options'


app = appdaora([app_options, route_options], options=True)
