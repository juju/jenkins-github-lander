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

deps: venv
	bin/pip install -r requirements.txt

develop:
	bin/python jenkinsmerger/setup.py develop

run:
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
