install:
	poetry install

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

patch: check
	rm -Rvf dist/
	poetry install
	poetry version patch
	poetry build
	poetry publish --dry-run --username ' ' --password ' '

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=gendiff tests/ --cov-report xml

lint:
	poetry run flake8 gendiff
	poetry run flake8 tests
	poetry run mypy gendiff

selfcheck:
	poetry check

check: selfcheck test lint

build: check
	rm -Rvf dist/
	poetry build

.PHONY: install test lint selfcheck check build