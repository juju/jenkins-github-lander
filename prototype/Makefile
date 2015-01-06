# Makefile to help automate tasks
WD := $(shell pwd)
PY := bin/python
PIP := bin/pip
DEPS_CANARY := lib/.DEPS_CANARY

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


deps: $(DEPS_CANARY)
$(DEPS_CANARY): | venv
	bin/pip install -r requirements.txt
	touch $(DEPS_CANARY)

develop:
	bin/python jenkinsmerger/setup.py develop

.PHONY: devrun
devrun:
	cd jenkinsmerge
	../bin/pserve development.ini

# ###########
# Development
# ###########
.PHONY: clean_all
clean_all: clean_venv
	if [ -d dist ]; then \
        rm -r dist; \
    fi

.PHONY: run
run:
	paster

.PHONY: test
test:	deps
	bin/nosetests -x -s jenkinsmerger
