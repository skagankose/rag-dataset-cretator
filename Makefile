.PHONY: up down logs fmt lint test clean build

# Docker commands
up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

# Development commands
fmt:
	cd backend && black . && ruff format .
	cd frontend && npm run format

lint:
	cd backend && ruff check . && mypy .
	cd frontend && npm run lint

test:
	cd backend && pytest
	cd frontend && npm run test

clean:
	docker compose down --volumes --rmi all
	docker system prune -f

build:
	docker compose build --no-cache 