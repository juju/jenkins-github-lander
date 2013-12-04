from pyramid.config import Configurator
from pyramid.response import Response

from jenkinsgithublander.jobs import kick_mergeable_pull_requests


# Route callables
def trigger_mergable_commits(request):
    config = request.registry.settings
    kicked = kick_mergeable_pull_requests(config)
    if kicked:
        ret = "\n".join(kicked)
    else:
        ret = "No pull requests to merge."

    return Response(ret)


# Config
def main(global_config, **settings):
    # Add the github request info to the settings.
    config = Configurator(settings=settings)

    config.add_route('check_pulls', '/check_pulls')
    config.add_view(trigger_mergable_commits, route_name='check_pulls')

    return config.make_wsgi_app()
