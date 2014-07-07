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
    kicked = []
    for project, merge_job in config['projects'].iteritems():
        github_info = GithubInfo(
            config['github.owner'],
            project,
            config['github.username'],
            config['github.token'],
        )

        mergable = mergeable_pull_requests(
            config['jenkins.merge.trigger'],
            github_info,
        )

        if mergable:
            jenkins_info = JenkinsInfo(
                config['jenkins.merge.url'],
                merge_job,
                config['jenkins.merge.token'],
            )

            for pr in mergable:
                try:
                    kick_jenkins_merge(pr, jenkins_info)
                    kick_message = 'Kicking {} pull request: {} at sha {}'
                    kicked.append(kick_message.format(
                        project,
                        pr.number,
                        pr.head_sha,
                    ))

                    # Notify the pull request that we've scheduled a build for
                    # it.
                    jenkins_url = generate_job_url(jenkins_info)
                    pull_request_kicked(pr, jenkins_url, github_info)

                except JenkinsError as exc:
                    fail_message = 'Failed to kick {} #{}. Failure message: {}'
                    kicked.append(fail_message.format(
                        project,
                        pr.number,
                        exc,
                    ))

    return kicked


def mark_pull_request_build_failed(job_name, pr, build_number, failure_message,
                                   config):
    """The given pull request failed to build.

    Comment on the pull request to alert the devs of this issue.

    :param job_name: The Jenkins ENV var for $JOB_NAME
    :param pr: The pull request number from the parameterized build.
    :param build_nubmer: The jenkins build number.

    """
    # Find the project by matching up the job_name from the Jenkins build.
    github_project = None
    for project, job in config['projects'].iteritems():
        if job == job_name:
            github_project = project

    github_info = GithubInfo(
        config['github.owner'],
        github_project,
        config['github.username'],
        config['github.token'],
    )
    jenkins_info = JenkinsInfo(
        config['jenkins.merge.url'],
        job_name,
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


def do_merge_pull_request(job_name, pr, build_number, config):
    """The given pull build passed and needs to be merged.

    """
    # Find the project by matching up the job_name from the Jenkins build.
    github_project = None
    for project, job in config['projects'].iteritems():
        if job == job_name:
            github_project = project

    github_info = GithubInfo(
        config['github.owner'],
        github_project,
        config['github.username'],
        config['github.token'],
    )
    jenkins_info = JenkinsInfo(
        config['jenkins.merge.url'],
        job_name,
        config['jenkins.merge.token'],
    )

    build_url = generate_build_url(build_number, jenkins_info)
    result = merge_pull_request(
        pr,
        build_url,
        github_info
    )
    if result.get("merged", False):
        return result['message']
    raise GithubError('Failed to merge: {0}'.format(result))
