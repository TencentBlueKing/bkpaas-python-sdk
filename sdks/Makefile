hyphen := -
empty :=
space := $(empty) $(empty)

.PHONY: poetry-git-tag
poetry-git-tag: poetry.lock
	$(eval tag = $(subst $(space),$(hyphen),$(shell poetry version)))
	git tag "${tag}"
