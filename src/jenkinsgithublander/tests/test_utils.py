from unittest import TestCase

from jenkinsgithublander.utils import build_config


class TestConfigUtils(TestCase):

    def test_build_config_single_project(self):
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
        fake_config = build_config(fake_config)

        self.assertIn('projects', fake_config)
        self.assertEqual(
            1, len(fake_config['projects']),
            'There is only one project in the list.')
        self.assertEqual(
            'juju-gui-merge', fake_config['projects']['juju-gui'])

    def test_build_config_multiple_projects(self):
        fake_config = {
            'github.owner': 'CanonicalJS',
            'github.project': 'juju-gui\njuju',
            'github.username': 'juju-gui',
            'github.token': '1234',
            'jenkins.merge.url': 'http://jenkins/job/{0}/build',
            'jenkins.merge.job': 'juju-gui-merge\njuju-merge',
            'jenkins.merge.token': 'buildme',
            'jenkins.merge.trigger': '$$merge$$',
        }
        fake_config = build_config(fake_config)

        self.assertIn('projects', fake_config)
        self.assertEqual(
            2, len(fake_config['projects']),
            'There are two project in the list.')
        self.assertEqual(
            'juju-gui-merge', fake_config['projects']['juju-gui'])
        self.assertEqual(
            'juju-merge', fake_config['projects']['juju'])

    def test_no_projects_blows_up(self):
        fake_config = {
            'github.owner': 'CanonicalJS',
            'github.project': '',
            'github.username': 'juju-gui',
            'github.token': '1234',
            'jenkins.merge.url': 'http://jenkins/job/{0}/build',
            'jenkins.merge.job': '',
            'jenkins.merge.token': 'buildme',
            'jenkins.merge.trigger': '$$merge$$',
        }

        self.assertRaises(ValueError, build_config, fake_config)

    def test_more_github_projects_blows_up(self):
        fake_config = {
            'github.owner': 'CanonicalJS',
            'github.project': 'juju-gui\njuju',
            'github.username': 'juju-gui',
            'github.token': '1234',
            'jenkins.merge.url': 'http://jenkins/job/{0}/build',
            'jenkins.merge.job': 'juju-gui-merge',
            'jenkins.merge.token': 'buildme',
            'jenkins.merge.trigger': '$$merge$$',
        }

        self.assertRaises(ValueError, build_config, fake_config)

    def test_more_jenkins_projects_blows_up(self):
        fake_config = {
            'github.owner': 'CanonicalJS',
            'github.project': 'juju-gui',
            'github.username': 'juju-gui',
            'github.token': '1234',
            'jenkins.merge.url': 'http://jenkins/job/{0}/build',
            'jenkins.merge.job': 'juju-gui-merge\njuju-merge',
            'jenkins.merge.token': 'buildme',
            'jenkins.merge.trigger': '$$merge$$',
        }

        self.assertRaises(ValueError, build_config, fake_config)
