FORCE_UPLOAD ?= 0

ifeq ("${FORCE_UPLOAD}", "1")
	FORCE_FLAG = --skip-existing
endif

.PHONY: build_package
build_package:
	python -m build

.PHONY: uplaod
upload: build_package
	twine upload ${FORCE_FLAG} $(shell ls -rt dist/*.whl | tail -n 1)

.PHONY: test
test:
	pytest --cov -s tests

.PHONY: req
req:
	pip install .
	pip install -e '.[dev]'
	pip install -e '.[build]'
