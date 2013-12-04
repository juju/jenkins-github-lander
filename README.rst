Jenkins Github Lander
==========================

Used to integrate Jenkins with Github to aid in auto landing branches that
have been reviewed and approved for landing into the 'trunk' branch of the
project.


Process
--------

- Pull request is created
- Code review happens and tests are run from an outside Jenkins job.
- Once code receives a LGTM, the author places a keyword "$$merge$$" into a
  final comment on the pull request.
- This webservice, via a hook notification Github, catches this and triggers a
  merge job in jenkins.
- If all tests pass, the Jenkins server will ping back that this pull request
  is good and passes all tests.
- This web service then triggers a merge via the Github api to land the branch.


Install on Jenkins Server
--------------------------

The service does not have to be, but it can be installed on your Jenkins
server. The steps below walk through a sample setup process.

::

    ssh ci.com
    sudo su jenkins
    cd ~
    git clone https://github.com/juju/jenkins-github-lander.git
    cd jenkins-github-lander
    make all
    make development.ini
    # Hack the ini settings for the jenkins server and the github project/bot user.

    # Add cron job per README

    # Add to the -merge job's build steps the final step of:
    cd /var/lib/jenkins/jenkins-github-lander && ./bin/lander-merge-result --ini development.ini --pr=${pr} --build=${BUILD_NUMBER}


Configuration
--------------

Update the INI file used to launch the web service with the following
configuration keys.


::

    jenkins.merge.url = http://ci.jujusomething.com/job/{}/buildWithParameters
    jenkins.merge.job = juju-gui-merge
    jenkins.merge.token = jenkinsbuildtoken
    jenkins.merge.trigger = $$merge$$

    github.apiurl = https://api.github.com
    github.username = github-bot
    github.token = github-bot-auth-token
    github.owner = Juju
    github.project = juju-gui


Triggering Merge from Jenkins
------------------------------

Jenkins is charged with running the actual build testing that a pull request
is correct and ready to merge. At the end of the build script for your job,
the service must be triggered with a command to either merge the pull request
or that a pull request build failed. In the case of a failure, the service
will add a comment to the pull request stating that, and linking back to the
Jenkins job to aid in debugging.

Success
~~~~~~~~

A build should exit on the first command in the build that returns a
non-successful error code. To indicate success, the command only needs to be
the last item in the build script.

Please indicate the pull request number so the script can properly close the
correct one. Also make sure to indicate the build number from Jenkins so that
the link to this build can be constructed.  The build number should be
available in the `ENV` within `$BUILD_NUMBER`.

Note that this is not to be run from the build. It will not have the correct
INI file.

::

    cd /$path/to/service/venv/ && \
    ./bin/lander-merge-result --ini development.ini --pr=5 --build=25


Failure
~~~~~~~~

To indicate a build has failed, you'll need to trigger the command after the
build has run and failed. There are a couple of different Jenkins plugins that
can assist with this.

  - https://wiki.jenkins-ci.org/display/JENKINS/PostBuildScript+Plugin
  - https://wiki.jenkins-ci.org/display/JENKINS/Post+build+task


Please indicate the pull request for updating. Also make sure to indicate the
build number from Jenkins so that the link to this build can be constructed.
The build number should be available in the `ENV` within `$BUILD_NUMBER`.

::

    cd /$path/to/service/venv/ && \
    ./bin/lander-merge-result --ini development.ini --failure="Build failed" --pr=5 --build=25


Running as a webservice
-----------------------

TBD


Running via cron
-----------------

You can run the service as a cron script to avoid needing to bring up a web
service. It will then just poll open pull requests for comments with the magic
landing trigger. In this case, then the jenkins build job must run the final
landing merge script vs ping'ing the web server with the url.

Since this is time based, and it polls all open pull requests, the order of
landing might not match the real order of comments on the pull requests.

::

    */3 * * * * cd /$path/to/service/venv/ && ./bin/lander-check-pulls --ini development.ini

Running webservice Manually
----------------------------
Currently the only way it works is to run manually. Copy the `sample.ini` file
into `development.ini` and update the config for your jenkins/github
configuration.

Once set, you can `make run` to start the webserver and the url
`/check_pulls` will become functional. If there are no pull requests that are
mergable, it'll respond so, and if it does kick off a merge job, it will reply
with the pull request id and the sha of the merge point.

::

    $ http://127.0.0.1:6543/check_pulls
    Kicking pull request: 5 at sha 089635fe2be2341cdbb8a3be093523798b918430
