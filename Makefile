# Makefile to help automate tasks
WD := $(shell pwd)
PY := bin/python

INI = development.ini

DEPS_CANARY := lib/.DEPS_CANARY
TESTDEPS_CANARY := lib/.TESTDEPS_CANARY

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
deps: $(DEPS_CANARY)
$(DEPS_CANARY): | venv
	bin/pip install -r requirements.txt
	touch $(DEPS_CANARY)

.PHONY: testdeps
testdeps: $(TESTDEPS_CANARY)
$(TESTDEPS_CANARY): | deps
	bin/pip install -r requirements.tests.txt
	touch $(TESTDEPS_CANARY)

EGG := lib/python2.7/site-packages/jenkins-github-lander.egg-link
$(EGG):
	bin/python setup.py develop

develop: venv $(EGG)

.PHONY: clean_all
clean_all: clean_venv
	if [ -d dist ]; then \
        rm -r dist; \
    fi

.PHONY: run
run: develop $(INI)
	bin/pserve development.ini

.PHONY: check
check: all testdeps lint test

.PHONY: test
test:
	bin/nosetests -x -s src/

bin/flake8: bin/python
	bin/pip install flake8

.PHONY: lint
lint: bin/flake8
	bin/flake8 src/jenkinsgithublander/
