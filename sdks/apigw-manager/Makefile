include ../Makefile

export PYTHONPATH=src

.PHONY: test
test:
	poetry run pytest -v --ds demo.settings --cov apigw_manager tests/

.PHONY: clean
clean:
	rm -rf build dist
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

.PHONY: tox
tox:
	poetry run tox

poetry.lock: pyproject.toml
	poetry lock --no-update

README.rst: README.md
	m2r --overwrite README.md

.PHONY: feature_test
feature_test:
	$(eval mock_server ?= http://yapi.example.com/mock/1)
	$(eval definition ?= definition.yaml)
	python manage.py fetch_apigw_public_key -p --host "${mock_server}"
	python manage.py sync_apigw_config --host "${mock_server}" -f "${definition}"
	python manage.py sync_apigw_stage --host "${mock_server}" -f "${definition}"
	python manage.py sync_apigw_strategies --host "${mock_server}" -f "${definition}"
	python manage.py sync_apigw_resources --host "${mock_server}" -f "${definition}"
	python manage.py apply_apigw_permissions --host "${mock_server}" -f "${definition}"
	python manage.py grant_apigw_permissions --host "${mock_server}" -f "${definition}"
	python manage.py create_version_and_release_apigw --host "${mock_server}" -f "${definition}"
	python manage.py sync_resource_docs_by_archive --host "${mock_server}" -f "${definition}"

.PHONY: build
build:
	rm -rf dist || true
	poetry build -f wheel

.PHONY: publish
publish:
	rm -rf dist || true
	poetry build -f wheel
	poetry publish -r pypi
	poetry publish -r tencent
