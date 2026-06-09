.PHONY: up down build seed lint test migrate shell

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

seed:
	docker compose exec backend python scripts/seed_experiments.py
	docker compose exec backend python scripts/seed_runs.py
	docker compose exec backend python scripts/seed_metrics.py

migrate:
	docker compose exec backend flask db upgrade

lint:
	ruff check backend/
	mypy backend/app
	cd frontend && npm run type-check

test:
	pytest backend/tests/ --cov=backend/app --cov-report=xml -v
	cd frontend && npm test

shell:
	docker compose exec backend flask shell

logs:
	docker compose logs -f
