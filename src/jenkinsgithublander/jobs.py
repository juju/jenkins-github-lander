from jenkinsgithublander.github import (
    GithubInfo,
    mergeable_pull_requests,
    pull_request_kicked,
)
from jenkinsgithublander.jenkins import (
    JenkinsError,
    JenkinsInfo,
    kick_jenkins_merge,
)


def merge_pull_requests(config):
    """Check github for pull requests that include the merge command.

    If the merge command is found, the -merge job in jenkins is kicked to
    start running.

    :return kicked: The list of pull requests that were kicked.

    """
    github_info = GithubInfo(
        config['github.owner'],
        config['github.project'],
        config['github.username'],
        config['github.token'],
    )

    mergable = mergeable_pull_requests(
        config['jenkins.merge.trigger'],
        github_info,
    )

    kicked = []
    if mergable:
        jenkins_info = JenkinsInfo(
            config['jenkins.merge.url'],
            config['jenkins.merge.job'],
            config['jenkins.merge.token'],
        )

        for pr in mergable:
            try:
                kick_jenkins_merge(
                    pr['number'], pr['head']['sha'], jenkins_info)
                kicked.append('Kicking pull request: {} at sha {}'.format(
                    pr['number'], pr['head']['sha']
                ))

                # Notify the pull request that we've scheduled a build for it.
                jenkins_url = jenkins_info.url.format(jenkins_info.job)
                pull_request_kicked(pr, jenkins_url, github_info)

            except JenkinsError as exc:
                kicked.append(
                    'Failed to kick {0}. Failure message: {1}'.format(
                        pr['number'],
                        exc
                    )
                )

    return kicked
