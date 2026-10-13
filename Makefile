.DEFAULT_GOAL := help

.PHONY: help python neural r test lint format clean

help:
	@printf '%s\n' \
	  'python  Install/synchronize the Python development environment.' \
	  'neural  Install/synchronize Python plus the optional PyTorch extra.' \
	  'r       Initialize the project-local R/statnet environment.' \
	  'test    Run Python tests.' \
	  'lint    Run Ruff checks.' \
	  'format  Apply Ruff formatting.' \
	  'clean   Remove local Python test and lint caches.'

python:
	uv sync --extra dev

neural:
	uv sync --extra dev --extra neural

r:
	Rscript r/bootstrap_renv.R

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
