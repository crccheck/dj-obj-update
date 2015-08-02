VERSION=0.2.1

help:
	@echo "help"
	@echo "-------------------------------------------------------"
	@echo "make help     this help"
	@echo "make clean    remove temporary files"
	@echo "make test     run test suite"
	@echo "make release  prep a release and upload to PyPI"

test:
	django-admin.py test

clean:
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
release: clean version
	@git commit -am "bump version to v$(VERSION)"
	@git tag $(VERSION)
	@-pip install wheel > /dev/null
	python setup.py sdist bdist_wheel upload
