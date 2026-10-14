.DEFAULT_GOAL := help

.PHONY: help python neural r r-model-test test lint format clean phase2-status phase2-audits phase2-dry-run phase2-report phase2-static phase2-temporal-export

help:
	@printf '%s\n' \
	  'python  Install/synchronize the Python development environment.' \
	  'neural  Install/synchronize Python plus the optional PyTorch extra.' \
	  'r       Initialize the project-local R/statnet environment.' \
	  'r-model-test  Run base-R smoke tests for the ERGM model drivers.' \
	  'test    Run Python tests.' \
	  'lint    Run Ruff checks.' \
	  'format  Apply Ruff formatting.' \
	  'phase2-status  Report local data readiness and scientific gates.' \
	  'phase2-audits  Run all locally available, ungated Phase 2 source audits.' \
	  'phase2-dry-run  Show which Phase 2 source audits would run.' \
	  'phase2-report  Write one local report from completed audit metadata.' \
	  'phase2-static  Run one static Phase 2 pilot; pass options in ARGS="...".' \
	  'phase2-temporal-export  Export a bounded chronological panel; pass options in ARGS="...".' \
	  'clean   Remove local Python test and lint caches.'

python:
	uv sync --extra dev

neural:
	uv sync --extra dev --extra neural

r:
	Rscript r/bootstrap_renv.R

r-model-test:
	Rscript r/tests/test_model_drivers.R

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

phase2-status:
	uv run python scripts/20_phase2_status.py

phase2-audits:
	uv run python scripts/26_run_phase2.py

phase2-dry-run:
	uv run python scripts/26_run_phase2.py --dry-run

phase2-report:
	uv run python scripts/27_phase2_readiness_report.py

phase2-static:
	uv run python scripts/30_run_static_benchmark.py $(ARGS)

phase2-temporal-export:
	uv run python scripts/31_export_temporal_panel.py $(ARGS)

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
