check: lint test

lint:
	poetry check
	black --check .
	flake8
	mypy -p switter

test:
	pytest
