.PHONY: all
all: update

.PHONY: update
update:
	pip install -r requirements.txt

.PHONY: clean
clean:
	python clean.py --keep-project-data --keep-input-feature-data --keep-output-sounds

.PHONY: clean-all
clean-all:
	python clean.py --ensure-directories

.PHONY: test
test:
	nosetests

.PHONY: serve
serve:
	node node_server/server.js
