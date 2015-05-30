VERSION=0.0.0

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

release: clean version
	@-git commit -am "bump version to v$(VERSION)"
	@-git tag $(VERSION)
	@-pip install wheel > /dev/null
	python setup.py sdist bdist_wheel upload
