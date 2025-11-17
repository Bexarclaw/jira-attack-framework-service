# Makefile for JIRA Attack Framework Service

.PHONY: help install install-dev lint format type-check test coverage clean run setup sync export

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3
PIP := $(PYTHON) -m pip

# Directories
SRC_DIR := src
TEST_DIR := tests

help: ## Show this help message
	@echo "JIRA Attack Framework Service - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install production dependencies
	@echo "Installing production dependencies..."
	$(PIP) install -r requirements.txt
	@echo "✓ Production dependencies installed"

install-dev: install ## Install development dependencies
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements.txt
	@echo "✓ Development dependencies installed"

lint: ## Run code linters (ruff)
	@echo "Running ruff linter..."
	ruff check $(SRC_DIR) $(TEST_DIR)
	@echo "✓ Linting complete"

lint-fix: ## Run linters with auto-fix
	@echo "Running ruff with auto-fix..."
	ruff check --fix $(SRC_DIR) $(TEST_DIR)
	@echo "✓ Linting with auto-fix complete"

format: ## Format code with black
	@echo "Formatting code with black..."
	black $(SRC_DIR) $(TEST_DIR)
	@echo "✓ Code formatting complete"

format-check: ## Check code formatting
	@echo "Checking code formatting..."
	black --check $(SRC_DIR) $(TEST_DIR)
	@echo "✓ Format check complete"

type-check: ## Run type checking with mypy
	@echo "Running type checker..."
	mypy $(SRC_DIR)
	@echo "✓ Type checking complete"

test: ## Run tests with pytest
	@echo "Running tests..."
	pytest $(TEST_DIR) -v
	@echo "✓ Tests complete"

test-fast: ## Run tests without coverage
	@echo "Running tests (fast mode)..."
	pytest $(TEST_DIR) -v --no-cov
	@echo "✓ Tests complete"

coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "✓ Coverage report generated in htmlcov/"

clean: ## Clean up generated files
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "✓ Cleanup complete"

all: lint format type-check test ## Run all checks (lint, format, type-check, test)
	@echo "✓ All checks passed!"

check: lint-fix format type-check ## Run all checks with auto-fix
	@echo "✓ All checks complete!"

# Application commands
run: ## Run the CLI application
	@echo "Running attack2jira CLI..."
	$(PYTHON) -m src.main

init: ## Initialize configuration (.env file)
	@echo "Initializing configuration..."
	$(PYTHON) -m src.main init

setup: ## Set up JIRA project
	@echo "Setting up JIRA project..."
	$(PYTHON) -m src.main setup

sync: ## Sync ATT&CK techniques to JIRA
	@echo "Syncing techniques..."
	$(PYTHON) -m src.main sync

export: ## Export ATT&CK Navigator layer
	@echo "Exporting Navigator layer..."
	$(PYTHON) -m src.main export

status: ## Check configuration and connection status
	@echo "Checking status..."
	$(PYTHON) -m src.main status

# Development helpers
dev-setup: install-dev ## Complete development setup
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "✓ .env file created. Please edit with your credentials."; \
	else \
		echo ".env file already exists"; \
	fi
	@echo "✓ Development setup complete!"

watch-test: ## Run tests in watch mode (requires pytest-watch)
	@echo "Running tests in watch mode..."
	ptw -- $(TEST_DIR)

build: clean ## Build distribution package
	@echo "Building distribution package..."
	$(PYTHON) -m build
	@echo "✓ Build complete"

# CI/CD targets
ci-lint: ## CI: Run linting
	ruff check $(SRC_DIR) $(TEST_DIR) --output-format=github

ci-test: ## CI: Run tests with coverage
	pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=xml --cov-report=term

ci-all: ci-lint type-check ci-test ## CI: Run all checks
	@echo "✓ CI checks complete!"

# Docker targets (future)
docker-build: ## Build Docker image
	@echo "Docker support coming soon..."

docker-run: ## Run in Docker container
	@echo "Docker support coming soon..."

# Documentation targets (future)
docs: ## Generate documentation
	@echo "Documentation generation coming soon..."

docs-serve: ## Serve documentation locally
	@echo "Documentation serving coming soon..."

# Version management
version: ## Show current version
	@grep "version" pyproject.toml | head -1 | cut -d'"' -f2

# Quick development workflow
dev: lint-fix format test ## Quick dev workflow: fix, format, test
	@echo "✓ Development workflow complete!"
