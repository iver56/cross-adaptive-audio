.PHONY: all
all: update migrate

.PHONY: update
update:
	pip install -r requirements.txt
