.PHONY: help install dev up down logs build test clean restart

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server (API Gateway)
	python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

dev-mcp: ## Run MCP server directly
	python -m src.mcp.server

up: ## Start all services with Docker Compose
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs (use 'make logs SERVICE=api' for specific service)
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose logs -f; \
	else \
		docker-compose logs -f $(SERVICE); \
	fi

build: ## Build Docker images
	docker-compose build

rebuild: ## Rebuild and restart services
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

test-mcp: ## Run MCP client test
	python -m clients.mcp_client

test-http: ## Run HTTP client test
	python -m clients.http_client

clean: ## Clean up containers and volumes
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

ps: ## Show running containers
	docker-compose ps

shell: ## Open shell in API container
	docker-compose exec api /bin/bash

mysql: ## Connect to MySQL
	docker-compose exec mysql mysql -uroot -p$(MYSQL_PASSWORD) wedding_dress_db

redis-cli: ## Connect to Redis CLI
	docker-compose exec redis redis-cli
