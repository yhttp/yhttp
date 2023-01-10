PRJ = yhttp
PIP = pip3
HERE = $(shell readlink -f `dirname .`)
VENVNAME = $(shell basename $(HERE) | cut -d'-' -f1)
VENV = $(HOME)/.virtualenvs/$(VENVNAME)


.PHONY: venv
venv:
	python3 -m venv $(VENV)


.PHONY: env
env:
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .


.PHONY: cover
cover:
	pytest --cov=$(PRJ) tests


.PHONY: lint
lint:
	flake8


.PHONY: dist
dist:
	python setup.py sdist
