"""Helpers for interacting with Github api requests."""
from collections import namedtuple
import json
import requests
from textwrap import dedent

from jenkinsgithublander import LanderError
from jenkinsgithublander import logger

API_URL = 'https://api.github.com'
GithubInfo = namedtuple(
    'GithubInfo',
    ['owner', 'project', 'username', 'token'])
PullRequestInfo = namedtuple(
    "PullRequestInfo", [
        "number", "base_ref", "base_user", "head_ref", "head_sha",
        "head_repo_url", "comments_href",
    ])

MERGE_FAILED = 'Build failed: '
MERGE_SCHEDULED = 'merge request accepted'


class GithubError(LanderError):
    """Error interacting with the github api"""


def _build_url(route, request_info, extra_info=None):
    dict_request_info = dict(zip(request_info._fields, request_info))
    if extra_info:
        dict_request_info.update(extra_info)

    if not route.startswith('http'):
        route = API_URL + route

    url = route.format(**dict_request_info)

    if request_info.token:
        url += "?access_token=" + request_info.token

    return url


def _is_mergeable(comments, owner, trigger, request_info):
    """Determine if a given comment is a mergable request.

    :param comments: The list dict of the comments from the api.
    :param owner: The repos owner data from the api.
    :param trigger: The word/phrase to trigger a merge.
    :param request_info: The tuple of info to make a valid api request.

    """
    log = logger.getLogger()
    is_merging = False
    request_merge = False

    org = owner['login']

    for comment in comments:
        user = comment['user']['login']

        # Determine if a valid user has requested a merge.
        if trigger in comment['body']:
            if user_is_in_org(user, org, request_info):
                request_merge = True

        # However, is this merge already happening?
        if MERGE_SCHEDULED in comment['body']:
            is_merging = True

        # Reset the status if a requested merge failed.
        if is_merging:
            if MERGE_FAILED in comment['body']:
                request_merge = False
                is_merging = False
            else:
                log.debug("    PR is already merging")
    if not request_merge:
        log.debug("    No request for merge")
    return request_merge and not is_merging


def _json_resp(response):
    """Given a response, return the json of the resp and check for errors."""
    if str(response.status_code).startswith('20'):
        return response.json()
    else:
        raise GithubError(response.content)


def _get_paginated_results(url):
    """Return concatenated list of json from all pages based on given url."""
    results = []
    while True:
        resp = requests.get(url)
        results.extend(_json_resp(resp))
        if "next" not in resp.links:
            break
        url = resp.links["next"]["url"]
    return results


def get_open_pull_requests(request_info):
    """Return the list of open pull requests on the given project.

    :param request_info: a GithubInfo tuple.

    """
    path = "/repos/{owner}/{project}/pulls"
    url = _build_url(path, request_info)
    resp = requests.get(url)
    return _get_paginated_results(url)


def get_pull_request(number, request_info):
    path = "/repos/{owner}/{project}/pulls/{pr_number}"
    url = _build_url(path, request_info, extra_info={
        'pr_number': number
    })
    resp = requests.get(url)
    return _json_resp(resp)


def get_pull_request_comments(url, request_info):
    # The url already starts with https://api...
    url = _build_url(url, request_info)
    return _get_paginated_results(url)


def make_pull_request_info(json):
    """Wrap pull request json in PullRequestInfo object"""

    # If the user deletes the source repo that is referenced in the pull
    # request, then ignore it.
    repo = json["head"]["repo"]
    if repo is None:
        return None
    return PullRequestInfo(
        number=json["number"],
        base_ref=json["base"]["ref"],
        base_user=json["base"]["user"],
        head_ref=json["head"]["ref"],
        head_sha=json["head"]["sha"],
        head_repo_url=repo["clone_url"],
        comments_href=json["_links"]["comments"]["href"],
    )


def mergeable_pull_requests(trigger_word, request_info):
    """Find the links to the issue comments where a command to merge lives."""
    log = logger.getLogger()
    prs = get_open_pull_requests(request_info)
    mergable_prs = []

    if prs:
        for pr in prs:
            log.debug("  Checking PR {}".format(pr['number']))
            pr_info = make_pull_request_info(pr)
            if pr_info is None:
                log.debug("    Cannot get PR info")
                continue
            comments = get_pull_request_comments(
                pr_info.comments_href,
                request_info,
            )

            if comments:
                owner = pr_info.base_user
                if _is_mergeable(
                        comments, owner, trigger_word, request_info):
                    mergable_prs.append(pr_info)
            else:
                log.debug("    No comments")
    return mergable_prs


def merge_pull_request(pr_number, jenkins_url, request_info):
    """Given a passing build, trigger a merge on this pull request."""
    merge_url = "/repos/{owner}/{project}/pulls/{pr_number}/merge"
    pr = get_pull_request(pr_number, request_info)
    url = _build_url(merge_url, request_info, {
        'pr_number': pr_number,
    })

    commit_message = pr['title'].strip()
    if pr['body']:
        commit_message += "\n\n" + pr['body']
    resp = requests.put(
        url,
        data=json.dumps({
            'commit_message': commit_message,
        })
    )

    try:
        return _json_resp(resp)
    except GithubError as exc:
        # A failed merge will result in a 405 response which is an error.
        # There could also be another error, such as a limit hit on the number
        # of api connections. We attempt to decode and return the original
        # merge fail response, but reraise any others.
        try:
            payload = json.loads(str(exc))
            return payload
        except ValueError:
            raise exc


def pull_request_build_failed(pr, build_url, failure_message, request_info):
    """Notify the pull request that the merge job has failed to build"""
    comments_url = pr['_links']['comments']['href']
    url = _build_url(comments_url, request_info)
    comment_body = """Build failed: {0}
        build url: {1}
    """.format(failure_message, build_url)

    return _json_resp(
        requests.post(
            url,
            data=json.dumps({
                'body': dedent(comment_body)
            })
        )
    )


def pull_request_kicked(pr_info, jenkins_url, request_info):
    """Notify the pull request that the merge job has been kicked."""
    url = _build_url(pr_info.comments_href, request_info)
    comment_body = "Status: {0}. Url: {1}".format(
        MERGE_SCHEDULED,
        jenkins_url)

    return _json_resp(
        requests.post(
            url,
            data=json.dumps({
                'body': comment_body
            })
        )
    )


def user_is_in_org(user, org, request_info):
    """Check if a user is in a specific org."""
    log = logger.getLogger()
    path = '/users/{0}/orgs'.format(user)
    url = _build_url(path, request_info)
    resp = _json_resp(requests.get(url))
    orgs = [o['login'] for o in resp]
    if org in orgs:
        return True
    log.debug("    user {} not in {}".format(user, org))
    log.debug("    user's orgs: {}".format(orgs))
    log.debug("    Ensure {}'s membership in {} is public".format(
            user,org))
    return False
