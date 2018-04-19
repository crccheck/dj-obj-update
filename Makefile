VERSION=0.3.0

help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

test: ## Run test suite
	PYTHONPATH=. django-admin.py test --settings=test_settings

tdd: ## Run test suite with a watcher
	nodemon -e py -x "make test || true"

clean: ## Remove temporary files
	rm -rf MANIFEST
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name "*.pyc" -delete

version:
	@sed -i -r /version/s/[0-9.]+/$(VERSION)/ setup.py
	@sed -i -r /__version__/s/[0-9.]+/$(VERSION)/ obj_update.py

# Release instructions
# 1. bump VERSION above
# 2. run `make release`
# 3. `git push --tags origin master`
# 4. update release notes
release: ## Cut a release and upload to PyPI
release: clean version
	@git commit -am "bump version to v$(VERSION)"
	@git tag $(VERSION)
	@-pip install wheel > /dev/null
	python setup.py sdist bdist_wheel upload
