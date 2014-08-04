.DEFAULT_GOAL := all
.PHONY: reset test

all: test

test: reset

reset:
	-yes y | pip uninstall --exists-action=w django-futures
	pip install --exists-action=w --pre --no-deps ../src/
