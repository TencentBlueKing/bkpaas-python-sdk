include ../Makefile

.PHONY: build
build:
	rm -rf dist || true
	poetry build

.PHONY: publish
publish: build
	poetry publish -r pypi
	poetry publish -r tencent
