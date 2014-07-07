"""Helpers for interacting with Jenkins server."""
from collections import namedtuple
import requests


JenkinsInfo = namedtuple(
    'JenkinsInfo',
    ['url', 'job', 'token'])


class JenkinsError(Exception):
    pass


def generate_build_url(number, config):
    url = config.url.format(config.job)
    url = url + '/{0}'.format(number)
    return url


def generate_job_url(config):
    url = config.url
    return url.format(config.job)


def generate_job_build_url(config):
    url = config.url + '/buildWithParameters'
    return url.format(config.job)


def kick_jenkins_merge(pr_info, jenkins_info):
    """Trigger a merge build for the pull request specified"""
    url = generate_job_build_url(jenkins_info)
    request_data = {
        'pr': pr_info.number,
        'base': pr_info.base_ref,
        'ref': pr_info.head_ref,
        'sha1': pr_info.head_sha,
        'repo': pr_info.head_repo_url,
        'token': jenkins_info.token,
    }

    resp = requests.post(url, request_data)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise JenkinsError(resp.content)
