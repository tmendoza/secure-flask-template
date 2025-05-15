.PHONY: lint test run migrations

lint:
	black . && flake8

test:
	pytest --cov=app

run:
	flask run

migrations:
	python scripts/run_migrations.py
