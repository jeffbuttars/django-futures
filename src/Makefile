.DEFAUL_GOAL := all

all:
	$(MAKE) build

.PHONY: build cheese cheesewheel clean

build:
	python setup.py sdist

cheese:
	python setup.py sdist upload

# Use the wheel if have optional C extensions
# cheesewheel:
#     python setup.py sdist bdist_wheel upload

clean:
	rm -fr dist
	find . -iname '*.pyc' | xargs rm -fv
	find . -name '__pycache__' | xargs rm -fvr

test:
	echo "Write TESTS!!!!!!!!"
