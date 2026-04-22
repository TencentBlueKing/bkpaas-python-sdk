## Context

You are in the bkpaas-auth repo, helping implement features, fix bugs, and refactor existing code.

## Source code

* bkpaas-auth is a Django app that helps implement user authentication, used by BlueKing systems.
* The main project in `bkpaas_auth/`.
* Unit tests are placed in 'tests/' directory, following pytest conventions.

## Coding style

* For Python files, follow PEP-8.
* For Python files, run `ruff format` to format after edits.

## Common workflows

### Running tests

* Run all tests: `poetry run pytest -s`
* Run some tests: `poetry run pytest -s tests/filename.py`
* ALWAYS prefer specifying test files for efficiency.
