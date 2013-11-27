from pyramid.config import Configurator
from pyramid.response import Response

from jenkinsgithublander.github import mergeable_pull_requests
from jenkinsgithublander.github import GithubInfo
from jenkinsgithublander.jenkins import JenkinsInfo
from jenkinsgithublander.jenkins import kick_jenkins_merge


# Route callables

def trigger_mergable_commits(request):
    config = request.registry.settings
    mergable = mergeable_pull_requests(
        config['jenkins.merge.trigger'],
        GithubInfo(
            config['github.owner'],
            config['github.project'],
            config['github.username'],
            config['github.token'],
        )
    )

    if mergable:
        kicked = []
        jenkins_info = JenkinsInfo(
            config['jenkins.merge.url'],
            config['jenkins.merge.job'],
            config['jenkins.merge.token'],
        )

        for pr in mergable:
            kick_jenkins_merge(pr['number'], pr['head']['sha'], jenkins_info)

            kicked.append('Kicking pull request: {} at sha {}'.format(
                pr['number'], pr['head']['sha']
            ))
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
