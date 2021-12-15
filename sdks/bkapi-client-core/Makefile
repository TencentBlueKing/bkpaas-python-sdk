SRC_DIR := .
DEMO_DIR := ${SRC_DIR}/demo
PKG_DIR := ${SRC_DIR}/bkapi_client_core
TEST_DIR := ${SRC_DIR}/tests

.PHONY: ALL
ALL: poetry.lock version requirements_tox.txt requirements_dev.txt requirements.txt

poetry.lock: pyproject.toml
	poetry lock --no-update

bkapi_client_core/__init__.py: pyproject.toml
	poetry version | awk '{printf "__version__ = \"%s\"\n",$$2}' > ${PKG_DIR}/__init__.py

.PHONY: version
version: bkapi_client_core/__init__.py

requirements.txt: poetry.lock
	poetry export -f requirements.txt --without-hashes | grep -v "index-url" > requirements.txt

requirements_dev.txt: requirements.txt
	poetry export -f requirements.txt --without-hashes --dev | grep -v "index-url" > requirements_dev.txt

requirements_tox.txt: requirements_dev.txt
	grep -E 'pytest|mock|django' requirements_dev.txt > requirements_tox.txt

.PHONY: isort
isort:
	poetry run isort "${DEMO_DIR}" "${PKG_DIR}" "${TEST_DIR}"

.PHONY: black
black:
	poetry run black "${DEMO_DIR}" "${PKG_DIR}" "${TEST_DIR}"

.PHONY: black-check
black-check:
	poetry run black --check "${DEMO_DIR}" "${PKG_DIR}" "${TEST_DIR}"

.PHONY: flake8
flake8:
	poetry run pflake8 "${DEMO_DIR}" "${PKG_DIR}" "${TEST_DIR}"

.PHONY: mypy
mypy:
	poetry run mypy "${DEMO_DIR}"/*.py --strict
	poetry run mypy "${DEMO_DIR}" "${PKG_DIR}" "${TEST_DIR}"

.PHONY: linter
linter: isort black-check flake8 mypy

.PHONY: test
test:
	poetry run pytest "${DEMO_DIR}"
	poetry run pytest -v \
		--cov "${PKG_DIR}" \
		--cov-report xml \
		--no-cov-on-fail \
		--cov-fail-under=80 \
		"${SRC_DIR}/tests"

.PHONY: publish
publish: ALL
	rm -rf dist || true
	poetry build -f wheel
	poetry publish -r pypi
	poetry publish -r tencent

.PHONY: tox
tox:
	tox
