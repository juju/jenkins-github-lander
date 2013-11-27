"""Helpers for interacting with Github api requests."""
from collections import namedtuple
import requests


API_URL = 'https://api.github.com'
GithubInfo = namedtuple(
    'GithubInfo',
    ['owner', 'project', 'username', 'token'])


class GithubError(Exception):
    pass


def _build_url(route, request_info):
    dict_request_info = dict(zip(request_info._fields, request_info))

    if not route.startswith('http'):
        route = API_URL + route

    url = route.format(**dict_request_info)

    if request_info.token:
        url += "?access_token=" + request_info.token

    return url


def _json_resp(response):
    """Given a response, return the json of the resp and check for errors."""
    if response.status_code == 200:
        return response.json()
    else:
        raise GithubError(response.content)


def get_open_pull_requests(request_info):
    """Return the list of open pull requests on the given project.

    :param request_info: a GithubInfo tuple.

    """
    path = "/repos/{owner}/{project}/pulls"
    url = _build_url(path, request_info)
    resp = requests.get(url)
    return _json_resp(resp)


def get_pull_request_comments(url, request_info):
    # The url already starts with https://api...
    url = _build_url(url, request_info)
    resp = requests.get(url)
    return _json_resp(resp)


def mergeable_pull_requests(trigger_word, request_info):
    """Find the links to the issue comments where a command to merge lives."""
    prs = get_open_pull_requests(request_info)
    mergable_prs = []

    if prs:
        for pr in prs:
            comments = get_pull_request_comments(
                pr['_links']['comments']['href'],
                request_info
            )

            if comments:
                for comment in comments:
                    if trigger_word in comment['body']:
                        mergable_prs.append(pr)

    return mergable_prs
