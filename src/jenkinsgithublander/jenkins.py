"""Helpers for interacting with Jenkins server."""
from collections import namedtuple
import requests


JenkinsInfo = namedtuple(
    'JenkinsInfo',
    ['url', 'job', 'token'])


class JenkinsError(Exception):
    pass


def kick_jenkins_merge(pr_id, git_sha, jenkins_info):
    """Trigger a merge build for the pull request specified"""
    url = jenkins_info.url.format(jenkins_info.job)
    request_data = {
        'pr': pr_id,
        'sha1': git_sha,
        'token': jenkins_info.token,
    }

    resp = requests.post(url, request_data)
    if resp.status_code != 200:
        raise JenkinsError(resp.content)
