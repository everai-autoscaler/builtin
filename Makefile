.PHONY: build_package
build_package:
	python -m build

.PHONY: uplaod
upload: build_package
	twine upload $(shell ls dist/*.whl | sort -r | head -n 1)

.PHONY: test
test:
	pytest --cov -s tests

.PHONY: req
req:
	pip install .
	pip install -e '.[dev]'
	pip install -e '.[build]'
