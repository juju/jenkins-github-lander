import json
import mock
import responses
from unittest import TestCase

from jenkinsgithublander.github import GithubError
from jenkinsgithublander.jobs import (
    kick_mergeable_pull_requests,
    mark_pull_request_build_failed,
    do_merge_pull_request,
)
from jenkinsgithublander.utils import build_config
from jenkinsgithublander.tests.utils import load_data


class TestJobs(TestCase):

    def _get_fake_config(self):
        fake_config = {
            'github.owner': 'CanonicalJS',
            'github.project': 'juju-gui',
            'github.username': 'juju-gui',
            'github.token': '1234',
            'jenkins.merge.url': 'http://jenkins/job/{0}/build',
            'jenkins.merge.job': 'juju-gui-merge',
            'jenkins.merge.token': 'buildme',
            'jenkins.merge.trigger': '$$merge$$',
        }
        return build_config(fake_config)

    @responses.activate
    def test_merge_pull_request_kicker(self):
        # Fake out the data for the github requests.
        pulls = load_data('github-open-pulls.json')
        orgs = load_data('github-user-orgs.json')
        comments = load_data('github-pull-request-comments.json')
        new_comment = load_data('github-new-issue-comment.json')

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
        responses.add(
            responses.POST,
            (
                u'https://api.github.com/repos/CanonicalJS/juju-gui/issues/5/'
                u'comments'
            ),
            body=new_comment,
            status=200,
            content_type='application/json'
        )

        fake_config = self._get_fake_config()

        with mock.patch('jenkinsgithublander.jobs.kick_jenkins_merge'):
            kicked = kick_mergeable_pull_requests(fake_config)

        self.assertEqual(1, len(kicked))
        self.assertTrue(
            kicked[0].startswith('Kicking juju-gui pull request: 5 at sha '))

    @responses.activate
    def test_mark_pull_request_build_failed(self):
        # Fake out the data for the github requests.
        pull_request = 5
        build_number = 10
        pulls = load_data('github-open-pulls.json', load_json=True)
        comment = load_data('github-new-issue-comment.json', load_json=True)
        pull_data = pulls[0]

        # Will need to mock out the pull request get, the comment response.
        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/5',
            body=json.dumps(pull_data),
            status=200,
            content_type='application/json'
        )
        responses.add(
            responses.POST,
            (
                u'https://api.github.com/repos/CanonicalJS/juju-gui/issues/5/'
                u'comments'
            ),
            body=json.dumps(comment),
            status=200,
            content_type='application/json'
        )

        fake_config = self._get_fake_config()

        resp = mark_pull_request_build_failed(
            'juju-gui-merge',
            pull_request,
            build_number,
            'build Failed',
            fake_config
        )

        self.assertTrue(resp.startswith('https://api.github.com'))

    @responses.activate
    def test_merge_pull_request(self):
        # Fake out the data for the github requests.
        pull_request = 5
        build_number = 10
        merged = load_data('github-merge-success.json')
        pulls = load_data('github-open-pulls.json', load_json=True)
        pull_request_data = pulls[0]

        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/5',
            body=json.dumps(pull_request_data),
            status=200,
            content_type='application/json'
        )
        # Will need to mock out the pull request get, the comment response.
        responses.add(
            responses.PUT,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/5/merge',
            body=merged,
            status=200,
            content_type='application/json'
        )

        fake_config = self._get_fake_config()

        resp = do_merge_pull_request(
            'juju-gui-merge',
            pull_request,
            build_number,
            fake_config
        )

        self.assertEqual('Pull Request successfully merged', resp)

    @responses.activate
    def test_pull_request_missing_merge_field(self):
        # Fake out the data for the github requests.
        pull_request = 5
        build_number = 10
        merged = load_data('github-merge-not-mergeable.json')
        pulls = load_data('github-open-pulls.json', load_json=True)
        pull_request_data = pulls[0]

        responses.add(
            responses.GET,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/5',
            body=json.dumps(pull_request_data),
            status=200,
            content_type='application/json'
        )
        # Will need to mock out the pull request get, the comment response.
        responses.add(
            responses.PUT,
            'https://api.github.com/repos/CanonicalJS/juju-gui/pulls/5/merge',
            body=merged,
            status=200,
            content_type='application/json'
        )

        fake_config = self._get_fake_config()

        self.assertRaisesRegexp(GithubError, "^Failed to merge: ",
            do_merge_pull_request,
            'juju-gui-merge',
            pull_request,
            build_number,
            fake_config
        )
