from jenkinsgithublander.github import mergeable_pull_requests
from jenkinsgithublander.github import GithubInfo
from jenkinsgithublander.jenkins import JenkinsInfo
from jenkinsgithublander.jenkins import kick_jenkins_merge


def merge_pull_requests(config):
    """Check github for pull requests that include the merge command.

    If the merge command is found, the -merge job in jenkins is kicked to
    start running.

    :return kicked: The list of pull requests that were kicked.

    """
    mergable = mergeable_pull_requests(
        config['jenkins.merge.trigger'],
        GithubInfo(
            config['github.owner'],
            config['github.project'],
            config['github.username'],
            config['github.token'],
        )
    )

    kicked = []
    if mergable:
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
    return kicked
