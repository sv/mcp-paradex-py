.PHONY: format lint typecheck install-dev pre-commit clean test test-cov

# Install development dependencies
install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Format code with black
format:
	black src tests

# Lint code with ruff
lint:
	ruff check src tests --fix

# Type check with mypy
typecheck:
	mypy src

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=mcp_paradex --cov-report=html

# Run all checks including tests
check: format lint typecheck test

# Run pre-commit on all files
pre-commit:
	pre-commit run --all-files

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
