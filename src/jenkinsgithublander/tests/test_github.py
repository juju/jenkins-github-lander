"""Testing the github helpers work properly"""
import json
import responses
from unittest import TestCase

from jenkinsgithublander import (
    github,
    LanderError,
)
from jenkinsgithublander.github import (
    get_open_pull_requests,
    GithubInfo,
    GithubError,
    merge_pull_request,
    mergeable_pull_requests,
    pull_request_build_failed,
    pull_request_kicked,
)
from jenkinsgithublander.tests.utils import load_data


class TestGithubError(TestCase):

    def test_github_error(self):
        """A GithubError can be made, stringified, and is a LanderError"""
        e = GithubError("Test error")
        self.assertEqual(str(e), "Test error")
        self.assertIsInstance(e, LanderError)


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
    def test_user_is_not_in_org(self):
        user_orgs = load_data('github-user-orgs.json')
        responses.add(
            responses.GET,
            'https://api.github.com/users/jujugui/orgs',
            body=user_orgs,
            status=200,
            content_type='application/json'
        )

        info = GithubInfo('juju', 'gui', 'jujugui', '1234')
        in_org = github.user_is_in_org('jujugui', 'noexist', info)

        self.assertFalse(in_org)

    @responses.activate
    def test_user_is_in_org(self):
        user_orgs = load_data('github-user-orgs.json')
        responses.add(
            responses.GET,
            'https://api.github.com/users/jujugui/orgs',
            body=user_orgs,
            status=200,
            content_type='application/json'
        )

        info = GithubInfo('juju', 'gui', 'jujugui', '1234')
        in_org = github.user_is_in_org('jujugui', 'CanonicalJS', info)

        self.assertTrue(in_org)

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
    def test_not_mergeable_if_not_in_org(self):
        pulls = load_data('github-open-pulls.json')
        orgs = load_data('github-user-orgs.json', load_json=True)
        comments = load_data('github-pull-request-comments.json')

        # Remove the CanonicalJS group so that the user fails to be in the
        #org.
        orgs.pop(0)

        responses.add(
            responses.GET,
            'https://api.github.com/users/mitechie/orgs',
            body=json.dumps(orgs),
            status=200,
            content_type='application/json'
        )

        responses.add(
            responses.GET,
            'https://api.github.com/repos/juju/project/pulls',
            body=pulls,
            status=200,
            content_type='application/json'
        )

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

        self.assertEqual(0, len(mergeable))

    @responses.activate
    def test_not_mergable_if_already_merging(self):
        pulls = load_data('github-open-pulls.json')
        orgs = load_data('github-user-orgs.json')
        comments = load_data(
            'github-pull-request-comments.json', load_json=True)

        # Add the currently merging comment to the list of the pull request to
        # verify it does not mark this as a mergable pull request then.
        merging_comment = load_data(
            'github-new-issue-comment.json', load_json=True)
        comments.append(merging_comment)

        responses.add(
            responses.GET,
            'https://api.github.com/users/mitechie/orgs',
            body=orgs,
            status=200,
            content_type='application/json'
        )
        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls',
            body=pulls,
            status=200,
            content_type='application/json'
        )
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

        info = GithubInfo('CanonicalJS', 'juju-gui', 'jujugui', None)
        mergeable = mergeable_pull_requests('$$merge$$', info)

        self.assertEqual(0, len(mergeable))

    @responses.activate
    def test_mergeable_pull_requests(self):
        pulls = load_data('github-open-pulls.json')
        orgs = load_data('github-user-orgs.json')
        comments = load_data('github-pull-request-comments.json')

        responses.add(
            responses.GET,
            'https://api.github.com/users/mitechie/orgs',
            body=orgs,
            status=200,
            content_type='application/json'
        )
        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls',
            body=pulls,
            status=200,
            content_type='application/json'
        )
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

        info = GithubInfo('CanonicalJS', 'juju-gui', 'jujugui', None)
        mergeable = mergeable_pull_requests('$$merge$$', info)

        self.assertEqual(1, len(mergeable))
        self.assertEqual(5, mergeable[0]['number'])

    @responses.activate
    def test_merge_pull_request(self):
        merge_response = load_data('github-merge-success.json')
        pulls = load_data('github-open-pulls.json', load_json=True)
        pull_request = pulls[0]

        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/4',
            body=json.dumps(pull_request),
            status=200,
            content_type='application/json'
        )
        responses.add(
            responses.PUT,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/4/merge',
            body=merge_response,
            status=200,
            content_type='application/json'
        )

        info = GithubInfo('CanonicalJS', 'juju-gui', 'jujugui', None)
        result = merge_pull_request(
            4,
            'http://jenkins.com/job/gui/12',
            info
        )

        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[0].request.method, "GET")
        self.assertEqual(responses.calls[1].request.method, "PUT")
        self.assertEqual(responses.calls[1].request.body,
                         '{"commit_message": "Update hacking\\n\\nhere are the changes requested."}')

        self.assertEqual(True, result['merged'])
        self.assertEqual("Pull Request successfully merged", result['message'])

    @responses.activate
    def test_merge_pull_request_fails(self):
        merge_response = load_data('github-merge-failed.json')
        pulls = load_data('github-open-pulls.json', load_json=True)
        pull_request = pulls[0]

        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/4',
            body=json.dumps(pull_request),
            status=200,
            content_type='application/json'
        )

        responses.add(
            responses.PUT,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/4/merge',
            body=merge_response,
            status=405,
            content_type='application/json'
        )

        info = GithubInfo('CanonicalJS', 'juju-gui', 'jujugui', None)
        result = merge_pull_request(
            4,
            'http://jenkins.com/job/gui/12',
            info
        )

        self.assertEqual(False, result['merged'])
        self.assertEqual("Failure reason", result['message'])

    @responses.activate
    def test_merge_pull_request_fail_unplanned(self):
        """Still throws exception on expected request failure."""
        pulls = load_data('github-open-pulls.json', load_json=True)
        pull_request = pulls[0]

        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/4',
            body=json.dumps(pull_request),
            status=200,
            content_type='application/json'
        )
        responses.add(
            responses.PUT,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/4/merge',
            body='Not Found',
            status=404,
            content_type='application/json'
        )

        info = GithubInfo('CanonicalJS', 'juju-gui', 'jujugui', None)

        self.assertRaises(
            GithubError,
            merge_pull_request,
            4,
            'http://jenkins.com/job/gui/12',
            info
        )

    @responses.activate
    def test_pull_request_build_failed(self):
        """Adds a comment to the pull request about the failure."""
        new_comment = load_data('github-new-issue-comment.json')
        pulls = load_data('github-open-pulls.json', load_json=True)
        pull_request = pulls[0]

        responses.add(
            responses.POST,
            (
                u'https://api.github.com/repos/CanonicalJS/juju-gui/issues/5/'
                u'comments'
            ),
            body=new_comment,
            status=201,
            content_type='application/json'
        )

        info = GithubInfo('CanonicalJS', 'juju-gui', 'jujugui', '1234')

        result = pull_request_build_failed(
            pull_request,
            'http://jenkins.com/job/gui/12',
            'Failure message',
            info
        )

        self.assertTrue('body' in result)

    @responses.activate
    def test_pull_request_kicked(self):
        new_comment = load_data('github-new-issue-comment.json')
        pulls = load_data('github-open-pulls.json', load_json=True)
        pull_request = pulls[0]

        responses.add(
            responses.POST,
            (
                u'https://api.github.com/repos/CanonicalJS/juju-gui/issues/5/'
                u'comments'
            ),
            body=new_comment,
            status=201,
            content_type='application/json'
        )

        info = GithubInfo('juju', 'project', 'jujugui', None)
        resp = pull_request_kicked(pull_request, 'http://jenkins/job/1', info)
        comment = resp['body']
        self.assertIn(github.MERGE_SCHEDULED, comment)
