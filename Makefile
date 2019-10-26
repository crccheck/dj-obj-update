VERSION = $$(grep __version__ obj_update.py | sed -r 's/.*"([.0-9]*)".*/\1/')

help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

test: ## Run test suite
	PYTHONPATH=. django-admin.py test --settings=test_app.settings

tdd: ## Run test suite with a watcher
	nodemon -e py -x "make test || true"

lint: ## Check for lint errors
	black . --check

clean: ## Remove temporary files
	rm -rf MANIFEST
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

# Release instructions
# 1. bump the __version__ in `obj_update.py`
# 2. run `make release`
# 3. `git push --tags origin master`
# TODO generate a changelog
release: ## Cut a release and upload to PyPI
release: clean
	flit build
	@git commit -am "v$(VERSION)"
	@git tag $(VERSION)
	flit publish
