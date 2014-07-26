.DEFAUL_GOAL := all

all:
	$(MAKE) -C docs $@
	$(MAKE) -C src $@

.PHONY: clean test cheese
clean:
	$(MAKE) -C docs $@
	$(MAKE) -C src $@
	$(MAKE) -C devproject $@

test:
	$(MAKE) -C src $@

cheese:
	$(MAKE) -C src $@

cheesewheel:
	$(MAKE) -C src $@
