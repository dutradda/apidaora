export PYTHONPATH = .
export PROJECT_NAME = 'apidaora'
export VIRTUALENV = $(shell pwd)/venv

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

create-virtualenv:  ## Create virtualenv
	@virtualenv venv --python python3.7 --prompt '$(PROJECT_NAME)-> '

show-source-virtualenv:  ## Show source virtualenv command
	@echo "Run this command activate virtualenv:\n$$ source venv/bin/activate"
	@echo "\nTo deactivate run:\n$$ deactivate"

dependencies: _check-virtualenv ## Install dependencies
	@which flit >/dev/null || pip install flit
	@flit install --deps develop --extras all --symlink

build-docs: _check-virtualenv ## Build docs
	@mkdocs build
	@cp ./docs/changelog.md ./CHANGELOG.md
	@cd ./docs && ../scripts/replace-placeholders.py index.md ../README.md

serve-docs: _check-virtualenv ## Serve docs local
	@mkdocs serve

shell: _check-virtualenv ## Run ipython
	@ipython

check-code: isort black flake8 mypy

isort: _check-virtualenv ## Run isort saving changes
	@isort --recursive --apply $(PROJECT_NAME) docs/src

black: _check-virtualenv ## Run black saving changes
	@black $(PROJECT_NAME) docs/src

flake8: _check-virtualenv ## Run flake8
	@flake8 $(PROJECT_NAME) docs/src

mypy: _check-virtualenv ## Run mypy
	@mypy --strict $(PROJECT_NAME) # docs/src/index

tests-docs-examples: _check-virtualenv ## Run docs examples tests
	@docs/src/*/test.sh

tests-code: _check-virtualenv ## Run tests
	@pytest -xvv --cov $(PROJECT_NAME) --no-cov-on-fail \
		--cov-report=term-missing $(PROJECT_NAME)/tests

tests: tests-code tests-docs-examples ## Run all tests

integration: _check-virtualenv ## Run check-code and tests
	@make check-code
	@make tests

deploy-docs: build-docs  ## Deploy docs
	@mkdocs gh-deploy

deploy-pypi: _check-virtualenv ## Publish the package on pypi
	@flit publish

deploy: integration deploy-docs deploy-pypi  ## Run integration, deploy docs and deploy pypi

_check-virtualenv:
	@echo $(PATH) | grep "$(shell pwd)/venv/bin" >/dev/null || \
		( echo "Please run 'source venv/bin/activate' to activate virtualenv!\n" && exit 1 )

create-changelog:
	echo $(m) > changelog.d/$(shell uuidgen | cut -c 1-8).change

changelog-draft:
	@towncrier --draft

_update-version:
	@git checkout master && git pull
	@bumpversion $(v) --dry-run --no-commit --list | \
		grep new_version= | sed -e 's/new_version=//' | \
		xargs -n 1 towncrier --yes --version
	@make build-docs
	@git commit -am 'Update CHANGELOG'
	@bumpversion $(v)
	@echo "\nChangelog and version updated successfully"

update-version-major:
	@make _update-version v=major

update-version-minor:
	@make _update-version v=minor

update-version-patch:
	@make _update-version v=patch

push-version:
	@git push && git push --tags

build:
	@flit build
