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
# 2. run `make release`
# 3. `git push --tags origin master`
# 4. update release notes
release: ## Cut a release and upload to PyPI
release: clean
	@git commit -am "bump version to v$(VERSION)"
	@git tag $(VERSION)
	@-pip install wheel > /dev/null
	python setup.py sdist bdist_wheel upload
