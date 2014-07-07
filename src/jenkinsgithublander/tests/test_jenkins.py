import responses
from unittest import TestCase

from jenkinsgithublander.github import PullRequestInfo
from jenkinsgithublander.jenkins import (
    generate_build_url,
    generate_job_build_url,
    generate_job_url,
    kick_jenkins_merge,
    JenkinsError,
    JenkinsInfo,
)


class TestJenkinsHelpers(TestCase):

    def get_pr_info(self):
        return PullRequestInfo(4, "master", "auser", "abranch", "sha1232",
            "https://git.test", None)

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
        pr_info = self.get_pr_info()
        self.assertRaises(JenkinsError, kick_jenkins_merge, pr_info, info)

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
        result = kick_jenkins_merge(self.get_pr_info(), info)

        self.assertIsNone(result)

    @responses.activate
    def test_kick_jenkins_merge_201(self):
        responses.add(
            responses.POST,
            'http://jenkins.com/job/one/buildWithParameters',
            body='',
            status=201,
            content_type='application/json'
        )

        info = JenkinsInfo(
            'http://jenkins.com/job/{}', 'one', '1234')
        result = kick_jenkins_merge(self.get_pr_info(), info)

        self.assertIsNone(result)

    @responses.activate
    def test_kick_jenkins_merge_404(self):
        responses.add(
            responses.POST,
            'http://jenkins.com/job/one/buildWithParameters',
            body='',
            status=404,
            content_type='application/json'
        )

        info = JenkinsInfo(
            'http://jenkins.com/job/{}', 'one', '1234')
        pr_info = self.get_pr_info()
        self.assertRaises(JenkinsError, kick_jenkins_merge, pr_info, info)
