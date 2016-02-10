.PHONY: all
all: update

.PHONY: update
update:
	pip install -r requirements.txt

.PHONY: clean
clean:
	python clean.py --keep-project-data --keep-input-feature-data

.PHONY: clean-all
clean-all:
	python clean.py
