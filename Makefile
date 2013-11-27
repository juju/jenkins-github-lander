# Makefile to help automate tasks
WD := $(shell pwd)
PY := bin/python
PIP := bin/pip


# #######
# INSTALL
# #######
.PHONY: all
all: venv

venv: bin/python
bin/python:
	virtualenv .

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
run: develop
	bin/pserve development.ini


.PHONY: test
test:
	bin/nosetests -x -s src/
