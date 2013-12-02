"""Testing the github helpers work properly"""
import json
import responses
from unittest import TestCase

from jenkinsgithublander import github
from jenkinsgithublander.github import (
    get_open_pull_requests,
    mergeable_pull_requests,
    GithubInfo,
    GithubError,
)
from jenkinsgithublander.tests.utils import load_data


class TestGithubHelpers(TestCase):

    def test_build_url_helper(self):
        """Should build a url given a path and a GithubInfo Tuple"""
        info = GithubInfo('juju', 'gui', 'jujugui', '1234')
        path = "/repos/{owner}/{project}/pulls"

        url = github._build_url(path, info)

        self.assertEqual(
            'https://api.github.com/repos/juju/gui/pulls?access_token=1234',
            url)

    def test_build_url_helper_with_auth(self):
        """Should build a url given a path and a GithubInfo Tuple"""
        info = GithubInfo('juju', 'gui', 'jujugui', '1234')
        path = "/repos/{owner}/{project}/pulls"

        url = github._build_url(path, info)

        self.assertEqual(
            'https://api.github.com/repos/juju/gui/pulls?access_token=1234',
            url)

    @responses.activate
    def test_open_pull_requests_error(self):
        """Verify a non-200 throws an error"""
        responses.add(
            responses.GET,
            'https://api.github.com/repos/juju/nope/pulls',
            body='{"error": "not found"}',
            status=404,
            content_type='application/json'
        )

        info = GithubInfo('juju', 'nope', 'jujugui', '1234')
        self.assertRaises(GithubError, github.get_open_pull_requests, info)

    @responses.activate
    def test_open_pull_requests(self):
        """Verify we can parse the list."""
        resp_json = load_data('github-open-pulls.json')

        responses.add(
            responses.GET,
            'https://api.github.com/repos/juju/project/pulls',
            body=resp_json,
            status=200,
            content_type='application/json'
        )

        info = GithubInfo('juju', 'project', 'jujugui', None)
        open_requests = get_open_pull_requests(info)

        self.assertEqual(1, len(open_requests))
        self.assertTrue(
            open_requests[0]['_links']['comments']['href'].endswith(
                '/repos/CanonicalJS/juju-gui/issues/5/comments',
            )
        )

    @responses.activate
    def test_no_mergeable_pull_requests(self):
        pulls = load_data('github-open-pulls.json')

        responses.add(
            responses.GET,
            'https://api.github.com/repos/juju/project/pulls',
            body=pulls,
            status=200,
            content_type='application/json'
        )

        comments = load_data(
            'github-pull-request-comments.json',
            load_json=True)
        # Remove the first comment since it's the trigger one.
        comments.pop(0)

        responses.add(
            responses.GET,
            (
                u'https://api.github.com/repos/CanonicalJS/juju-gui/issues/5/'
                u'comments'
            ),
            body=json.dumps(comments),
            status=200,
            content_type='application/json'
        )

        info = GithubInfo('juju', 'project', 'jujugui', None)
        mergeable = mergeable_pull_requests('$$merge$$', info)

        self.assertEqual(0, len(mergeable))

    @responses.activate
    def test_mergeable_pull_requests(self):
        pulls = load_data('github-open-pulls.json')

        responses.add(
            responses.GET,
            'https://api.github.com/repos/juju/project/pulls',
            body=pulls,
            status=200,
            content_type='application/json'
        )

        comments = load_data('github-pull-request-comments.json')
        responses.add(
            responses.GET,
            (
                u'https://api.github.com/repos/CanonicalJS/juju-gui/issues/5/'
                u'comments'
            ),
            body=comments,
            status=200,
            content_type='application/json'
        )

        info = GithubInfo('juju', 'project', 'jujugui', None)
        mergeable = mergeable_pull_requests('$$merge$$', info)

        self.assertEqual(1, len(mergeable))
        self.assertEqual(5, mergeable[0]['number'])
