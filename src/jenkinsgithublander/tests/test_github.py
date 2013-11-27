"""Testing the github helpers work properly"""
import responses
from unittest import TestCase

from jenkinsgithublander import github
from jenkinsgithublander.github import GithubInfo
from jenkinsgithublander.github import GithubError


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
