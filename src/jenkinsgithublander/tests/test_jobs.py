import mock
import responses
from unittest import TestCase

from jenkinsgithublander.jobs import (
    merge_pull_requests,
)
from jenkinsgithublander.tests.utils import load_data


class TestJobs(TestCase):

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

        with mock.patch('jenkinsgithublander.jobs.kick_jenkins_merge'):
            kicked = merge_pull_requests(fake_config)

        self.assertEqual(1, len(kicked))
        self.assertTrue(
            kicked[0].startswith('Kicking pull request: 5 at sha '))
