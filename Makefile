.PHONY: dev test lint migrate help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[1m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Run FastAPI server locally
	PYTHONPATH=src uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests without Docker (uses mocks)
	uv run pytest .

lint: ## Lint and format code with Black + isort
	uv run black .

migrate: ## Run Alembic migrations
	uv run alembic upgrade head
