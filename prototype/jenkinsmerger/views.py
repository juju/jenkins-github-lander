from pyramid.view import view_config
import requests


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'jenkinsmerger'}


@view_config(route_name='check_pulls', renderer='json')
def check_pull_requests(request):
    """Fetch the list of pull requests and check if any are mergeable."""
    config = request.registry.settings
    results = []
    # The api defaults to open pull requests.
    url = "{}/repos/{}/{}/pulls?access_token={}"

    github_url = url.format(
        config.get('github.apiurl'),
        config.get('github.owner'),
        config.get('github.project'),
        config.get('github.token'),
    )
    resp = requests.get(github_url)
    pull_requests = resp.json()

    for pull in pull_requests:
        # Get the list of comments on the PR
        # They're under the issue created, not the pull request itself.
        comments_url = pull['_links']['comments']['href'] + "?access_token={}"

        resp = requests.get(comments_url.format(config.get('github.token')))
        comments = resp.json()

        jenkins_url = config.get('jenkins.merge.url')
        jenkins_payload = {
            'token': config.get('jenkins.merge.token'),
            'sha1': pull['head']['sha'],
            'pr': pull['number']
        }

        # Now we can check each of the comments to see if they contain the
        # magic phrase, and if so, request a build.
        # @Todo make sure the user is in the CanonicalJS org.
        for comment in comments:
            if config.get('jenkins.merge.trigger') in comment['body']:
                resp = requests.post(jenkins_url, params=jenkins_payload)
                results.append('Kicking merge for pull request: {}'.format(
                    pull['number']
                ))
            else:
                results.append('Not going to kick pull request: {}'.format(
                    pull['number']
                ))

    return results
