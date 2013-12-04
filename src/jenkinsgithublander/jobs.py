from jenkinsgithublander.github import (
    get_pull_request,
    GithubError,
    GithubInfo,
    merge_pull_request,
    mergeable_pull_requests,
    pull_request_build_failed,
    pull_request_kicked,
)
from jenkinsgithublander.jenkins import (
    generate_build_url,
    generate_job_url,
    JenkinsError,
    JenkinsInfo,
    kick_jenkins_merge,
)


def kick_mergeable_pull_requests(config):
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
                jenkins_url = generate_job_url(jenkins_info)
                pull_request_kicked(pr, jenkins_url, github_info)

            except JenkinsError as exc:
                kicked.append(
                    'Failed to kick {0}. Failure message: {1}'.format(
                        pr['number'],
                        exc
                    )
                )

    return kicked


def mark_pull_request_build_failed(pr, build_number, failure_message, config):
    """The given pull request failed to build.

    Comment on the pull request to alert the devs of this issue.

    """
    github_info = GithubInfo(
        config['github.owner'],
        config['github.project'],
        config['github.username'],
        config['github.token'],
    )
    jenkins_info = JenkinsInfo(
        config['jenkins.merge.url'],
        config['jenkins.merge.job'],
        config['jenkins.merge.token'],
    )

    pull_request = get_pull_request(pr, github_info)
    build_url = generate_build_url(build_number, jenkins_info)
    try:
        comment = pull_request_build_failed(
            pull_request,
            build_url,
            failure_message,
            github_info
        )
        return comment['url']
    except GithubError as exc:
        return 'Failed to add comment: {0}'.format(exc)


def do_merge_pull_request(pr, build_number, config):
    """The given pull build passed and needs to be merged.

    """
    github_info = GithubInfo(
        config['github.owner'],
        config['github.project'],
        config['github.username'],
        config['github.token'],
    )
    jenkins_info = JenkinsInfo(
        config['jenkins.merge.url'],
        config['jenkins.merge.job'],
        config['jenkins.merge.token'],
    )

    build_url = generate_build_url(build_number, jenkins_info)
    try:
        result = merge_pull_request(
            pr,
            build_url,
            github_info
        )
        if result['merged']:
            return result['message']
        else:
            raise GithubError(
                'Failed to merge: {0}'.format(result['message']))
    except GithubError as exc:
        return 'Failed to add comment: {0}'.format(exc)
