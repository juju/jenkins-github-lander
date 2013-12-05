import responses
from unittest import TestCase

from jenkinsgithublander.jenkins import (
    generate_build_url,
    generate_job_build_url,
    generate_job_url,
    kick_jenkins_merge,
    JenkinsError,
    JenkinsInfo,
)


class TestJenkinsHelpers(TestCase):

    def test_generate_build_url(self):
        build_num = 5
        info = JenkinsInfo(
            'http://jenkins.com/job/{}',
            'juju-gui',
            '1234')

        self.assertEqual(
            'http://jenkins.com/job/juju-gui/5',
            generate_build_url(build_num, info)
        )

    def test_generate_job_url(self):
        info = JenkinsInfo(
            'http://jenkins.com/job/{}',
            'juju-gui',
            '1234')

        self.assertEqual(
            'http://jenkins.com/job/juju-gui',
            generate_job_url(info)
        )

    def test_generate_job_build_url(self):
        info = JenkinsInfo(
            'http://jenkins.com/job/{}',
            'juju-gui',
            '1234')

        self.assertEqual(
            'http://jenkins.com/job/juju-gui/buildWithParameters',
            generate_job_build_url(info)
        )

    @responses.activate
    def test_missing_kick_jenkins_merge(self):
        responses.add(
            responses.POST,
            'http://jenkins.com/job/nope/buildWithParameters',
            body='{"error": "not found"}',
            status=404,
            content_type='application/json'
        )

        info = JenkinsInfo(
            'http://jenkins.com/job/{}', 'nope', '1234')
        self.assertRaises(JenkinsError, kick_jenkins_merge, 4, 'sha1232', info)

    @responses.activate
    def test_kick_jenkins_merge(self):
        responses.add(
            responses.POST,
            'http://jenkins.com/job/one/buildWithParameters',
            body='',
            status=200,
            content_type='application/json'
        )

        info = JenkinsInfo(
            'http://jenkins.com/job/{}', 'one', '1234')
        result = kick_jenkins_merge(4, 'sha1232', info)

        self.assertIsNone(result)
