#!make
.PHONY = init fmt migrate run

init:
	uv sync

fmt:
	uv run isort . && uv run black . && uv run ruff check . --fix

migrate:
	uv run python manage.py makemigrations && uv run python manage.py migrate

run:
	uv run python manage.py runserver
