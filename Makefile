# Makefile to help automate tasks
WD := $(shell pwd)
PY := bin/python

INI = development.ini

# #######
# INSTALL
# #######
.PHONY: all
all: venv deps develop

venv: bin/python
bin/python:
	virtualenv .

$(INI):
	cp sample.ini $(INI)

.PHONY: clean_venv
clean_venv:
	rm -rf bin include lib local man share

.PHONY: deps
deps: venv
	bin/pip install -r requirements.txt

.PHONY: testdeps
testdeps: deps
	bin/pip install -r requirements.tests.txt

lib/python*/site-packages/jenkins_github_lander.egg-link:
	bin/python setup.py develop
develop: venv lib/python*/site-packages/jenkins_github_lander.egg-link

.PHONY: clean_all
clean_all: clean_venv
	if [ -d dist ]; then \
        rm -r dist; \
    fi

.PHONY: run
run: develop $(INI)
	bin/pserve development.ini

.PHONY: test
test:
	bin/nosetests -x -s src/

bin/flake8:
	bin/pip install flake8

.PHONY: lint
lint: bin/flake8
	bin/flake8 src/jenkinsgithublander/
