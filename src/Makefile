.DEFAUL_GOAL := all

all:
	$(MAKE) build

.PHONY: build cheese cheesewheel clean

build:
	python setup.py sdist

cheese:
	python setup.py sdist upload

cheesewheel:
	python setup.py bdist_wheel upload

clean:
	rm -fr dist
	find . -iname '*.pyc' | xargs rm -fv
	find . -name '__pycache__' | xargs rm -fvr

test:
	echo "Write TESTS!!!!!!!!"
