from pyramid.config import Configurator
from pyramid.response import Response


# Route callables

def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)


# Config
def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.add_route('hello', '/hello/{name}')
    config.add_view(hello_world, route_name='hello')
    config.add_route('check_pulls', '/check_pulls')

    return config.make_wsgi_app()
