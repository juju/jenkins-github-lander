import pkg_resources

VERSION = pkg_resources.get_distribution("jenkins-github-lander").version

class LanderError(Exception):
    """Base exception type for jenkins github lander related errors"""
