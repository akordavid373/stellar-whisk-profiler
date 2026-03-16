# Stellar Whisk Parallelism Profiler Makefile

.PHONY: help install install-dev install-all test test-cov lint format type-check clean build upload docs serve-docs

# Default target
help:
	@echo "Stellar Whisk Parallelism Profiler - Available Commands:"
	@echo ""
	@echo "  install      Install package in development mode"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  install-all  Install package with all dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  type-check   Run type checking with mypy"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload       Upload package to PyPI"
	@echo "  docs         Generate documentation"
	@echo "  serve-docs   Serve documentation locally"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[dev,gpu,docs]"

# Development
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=stellar_whisk_profiler --cov-report=html --cov-report=term

lint:
	flake8 stellar_whisk_profiler/ tests/ examples/
	@echo "Linting completed"

format:
	black stellar_whisk_profiler/ tests/ examples/
	isort stellar_whisk_profiler/ tests/ examples/
	@echo "Code formatted"

type-check:
	mypy stellar_whisk_profiler/
	@echo "Type checking completed"

# Quality checks
check: lint type-check test
	@echo "All quality checks passed"

# Building and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "Build artifacts cleaned"

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

upload-test: build
	python -m twine upload --repository testpypi dist/*

# Documentation
docs:
	cd docs && make html

serve-docs:
	cd docs/_build/html && python -m http.server 8000

# Examples
run-examples:
	python examples/structured_example.py

run-stellar-examples:
	python examples/stellar_profiling.py

# Dashboard
start-dashboard:
	python -m stellar_whisk_profiler.frontend.app

# Development server
dev-server: install-dev
	python -m stellar_whisk_profiler.frontend.app

# Quick start for new users
quickstart: install-dev
	@echo "Running quick start examples..."
	python examples/structured_example.py
	@echo ""
	@echo "Quick start completed!"
	@echo "Run 'make start-dashboard' to open the web dashboard"

# Component-specific testing
test-backend:
	python -m pytest tests/test_backend.py -v

test-frontend:
	python -m pytest tests/test_frontend.py -v

test-contracts:
	python -m pytest tests/test_contracts.py -v

test-integration:
	python -m pytest tests/ -v -m integration

# Performance testing
perf-test:
	python -m stellar_whisk_profiler.cli profile --module examples/structured_example.py --function integrated_example --output perf_test_results.json

# Stellar-specific testing
test-stellar:
	python -m pytest tests/test_stellar_profiler.py -v

# Continuous integration
ci: install-all check test-cov test-backend test-frontend test-contracts
	@echo "CI pipeline completed successfully"

# Release preparation
prep-release: clean check test-cov build
	@echo "Release preparation completed"
	@echo "Run 'make upload' to publish to PyPI"

# Architecture documentation
show-architecture:
	@echo "Stellar Whisk Profiler Architecture:"
	@echo "├── frontend/     # Web dashboard and UI"
	@echo "├── backend/      # Core profiling engine and API"
	@echo "├── contracts/    # Stellar smart contracts and integration"
	@echo "└── stellar_whisk_profiler/  # Main package entry point"

# Development helpers
watch-test:
	watchdog --patterns="*.py" --recursive --command="make test"

serve-dashboard-dev:
	python -m stellar_whisk_profiler.frontend.app --host 0.0.0.0 --port 8080 --reload

# Component development
dev-backend:
	@echo "Backend development environment ready"
	@echo "Key files:"
	@echo "  - backend/profiler.py"
	@echo "  - backend/metrics.py"
	@echo "  - backend/collector.py"

dev-frontend:
	@echo "Frontend development environment ready"
	@echo "Key files:"
	@echo "  - frontend/app.py"
	@echo "  - frontend/routes.py"
	@echo "  - frontend/templates/"

dev-contracts:
	@echo "Contracts development environment ready"
	@echo "Key files:"
	@echo "  - contracts/profiler.py"
	@echo "  - contracts/metrics.py"
	@echo "  - contracts/collector.py"

# Benchmarking
benchmark:
	python -m stellar_whisk_profiler.cli profile --module examples/structured_example.py --function integrated_example --duration 30 --output benchmark_results.json

# Profiling the profiler itself
meta-profile:
	python -m cProfile -o meta_profile.stats -m stellar_whisk_profiler.cli profile --module examples/structured_example.py --function backend_example
	python -c "import pstats; p = pstats.Stats('meta_profile.stats'); p.sort_stats('cumulative').print_stats(20)"
