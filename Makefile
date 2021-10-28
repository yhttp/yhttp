PRJ = yhttp
PIP = pip3

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
