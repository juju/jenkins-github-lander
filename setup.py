from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1'

install_requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'requests',
    'waitress',
]

tests_require = [
    'nose',
    'mock',
    'responses',
]


setup(
    name='jenkins-github-lander',
    version=version,
    description=("Webservice to aid in landing branches to github after "
                 "jenkins tests pass"),
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='jenkins ci automated lander branch github',
    author='Rick Harding',
    author_email='rick.harding@canonical.com',
    url='https://github.com/juju/jenkins-github-lander',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points={
        'paste.app_factory': [
            'main = jenkinsgithublander.app:main'
        ],
        'console_scripts': [
            'jenkins-github-lander=jenkinsgithublander:main'
        ],
    },
)
