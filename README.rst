Jenkins Github Lander
==========================

Used to integrate Jenkins with Github to aid in auto landing branches that
have been reviewed and approved for landing into the 'trunk' branch of the
project.


Process
--------

- Pull request is created
- Code review happens and tests are run from an outside jenkins job.
- Once code receives a LGTM, the author places a keyword "$$merge$$" into a
  final comment on the pull request.
- This webservice, via a hook notification github, catches this and triggers a
  merge job in jenkins.
- If all tests pass, the jenkins server will ping back that this pull request
  is good and passes all tests.
- This web service then triggers a merge via the Github api to land the branch.


Configuration
--------------

Update the ini file used to launch the web service with the following
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

Running Manually
----------------
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
