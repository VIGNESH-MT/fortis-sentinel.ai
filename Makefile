.PHONY: help install install-backend install-frontend run run-backend run-frontend test lint format docker-up docker-down clean

help: ## Show this help message
	@echo "FORTIS SENTINEL v0.1.0 - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

run-backend: ## Run backend development server
	cd backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run frontend development server
	cd frontend && npm run dev

run: ## Run both backend and frontend (requires two terminals)
	@echo "Run 'make run-backend' in one terminal and 'make run-frontend' in another"

test: ## Run all tests
	cd backend && python -m pytest tests/ -v --cov=. --cov-report=term-missing

test-unit: ## Run unit tests only
	cd backend && python -m pytest tests/test_approaches/ tests/test_apis/ -v

test-integration: ## Run integration tests
	cd backend && python -m pytest tests/test_integration/ -v

lint: ## Run linters
	cd backend && python -m flake8 . --max-line-length=120 --exclude=venv,__pycache__
	cd frontend && npx eslint src/

format: ## Format code
	cd backend && python -m black . --line-length=120

docker-up: ## Start all services with Docker Compose
	docker-compose up -d --build

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/dist frontend/node_modules/.cache
