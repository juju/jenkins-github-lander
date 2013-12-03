import responses
from unittest import TestCase

from jenkinsgithublander.jenkins import (
    kick_jenkins_merge,
    JenkinsError,
    JenkinsInfo,
)


class TestJenkinsHelpers(TestCase):

    @responses.activate
    def test_missing_kick_jenkins_merge(self):
        responses.add(
            responses.POST,
            'http://jenkins.com/job/nope/buildWithArguments',
            body='{"error": "not found"}',
            status=404,
            content_type='application/json'
        )

        info = JenkinsInfo(
            'http://jenkins.com/job/{}/buildWithArguments', 'nope', '1234')
        self.assertRaises(JenkinsError, kick_jenkins_merge, 4, 'sha1232', info)

    @responses.activate
    def test_kick_jenkins_merge(self):
        responses.add(
            responses.POST,
            'http://jenkins.com/job/one/buildWithArguments',
            body='',
            status=200,
            content_type='application/json'
        )

        info = JenkinsInfo(
            'http://jenkins.com/job/{}/buildWithArguments', 'one', '1234')
        result = kick_jenkins_merge(4, 'sha1232', info)

        self.assertIsNone(result)
