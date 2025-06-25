# Makefile para Sales Command
.PHONY: help install test lint format type-check run clean dev-setup validate

# Variables
PYTHON := python
PIP := pip
UV := uv

help: ## Mostrar esta ayuda
	@echo "Sales Command - Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias
	$(PYTHON) -m venv venv
	$(PIP) install uv
	$(UV) sync --dev

test: ## Ejecutar tests
	$(UV) run pytest -v --cov=src

test-watch: ## Ejecutar tests en modo watch
	$(UV) run pytest-watch

lint: ## Verificar código con ruff
	$(UV) run ruff check .

format: ## Formatear código con ruff
	$(UV) run ruff format .

type-check: ## Verificar tipos con mypy
	$(UV) run mypy src/

run: ## Ejecutar la aplicación
	$(UV) run python -m src.main

dev-setup: ## Configuración completa de desarrollo
	$(MAKE) install
	$(UV) run pre-commit install
	$(PYTHON) validate_setup.py

validate: ## Validar configuración del proyecto
	$(PYTHON) validate_setup.py

clean: ## Limpiar archivos temporales
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage

build: ## Build del proyecto
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

init-db: ## Inicializar base de datos
	$(UV) run python -c "from src.database.connection import init_database; init_database()"

reset-db: ## Resetear base de datos
	$(UV) run python -c "from src.database.connection import reset_database; reset_database()"

demo: ## Datos de demostración
	$(UV) run python scripts/demo_data.py

# Comandos de desarrollo rápido
quick-test: ## Test rápido sin coverage
	$(UV) run pytest tests/test_basic.py -v

fix: ## Fix automático de problemas
	$(MAKE) format
	$(UV) run ruff check --fix .

check: ## Verificación completa
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
