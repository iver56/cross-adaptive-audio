.PHONY: all
all: update

.PHONY: update
update:
	pip install -r requirements.txt

.PHONY: clean
clean:
	python clean.py

.PHONY: prepare-ramdisk
prepare-ramdisk:
	python prepare_ramdisk.py

.PHONY: test
test:
	nosetests

.PHONY: serve
serve:
	python serve.py
