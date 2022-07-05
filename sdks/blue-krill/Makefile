include ../Makefile

.PHONY: build
build:
	rm -rf dist || true
	poetry build

.PHONY: publish
publish: build
	twine upload dist/* -r pypi
	twine upload dist/* -r tencent
