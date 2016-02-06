.PHONY: all
all: update

.PHONY: update
update:
	pip install -r requirements.txt

.PHONY: clean
clean:
	python clean.py
