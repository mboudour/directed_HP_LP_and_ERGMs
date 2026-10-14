.DEFAULT_GOAL := help

.PHONY: help python neural r r-model-test test lint format clean phase2-status phase2-audits phase2-dry-run phase2-report phase2-static phase2-export-masks phase2-eu-core-score phase2-temporal-export phase2-eu-core-temporal

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
	  'phase2-export-masks  Export existing pilot masks; pass options in ARGS="...".' \
	  'phase2-eu-core-score  Export pilot masks and score them with masked ERGM fits.' \
	  'phase2-temporal-export  Export a bounded chronological panel; pass options in ARGS="...".' \
	  'phase2-eu-core-temporal  Run the bounded EU-core lagged chronological check.' \
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

phase2-export-masks:
	uv run python scripts/32_export_static_pilot_masks.py $(ARGS)

phase2-eu-core-score:
	uv run python scripts/32_export_static_pilot_masks.py --pilot-dir results/phase2/eu_core_static_pilot
	Rscript r/models/score_masked_ergm.R --input-dir=results/phase2/eu_core_static_pilot --output-dir=results/models/eu_core_masked_ergm --models=M0,M1,M3a,M4c --estimate=MPLE --seed=20261013
	uv run python scripts/33_summarize_masked_ergm.py --input-dir results/models/eu_core_masked_ergm

phase2-temporal-export:
	uv run python scripts/31_export_temporal_panel.py $(ARGS)

phase2-eu-core-temporal:
	uv run python scripts/31_export_temporal_panel.py --dataset eu_core --panel-count 3 --output-dir results/phase2/eu_core_temporal_check
	Rscript r/models/temporal_lagged_check.R --input=results/phase2/eu_core_temporal_check/panel_edges.csv --nodes=results/phase2/eu_core_temporal_check/nodes.csv --output-dir=results/models/eu_core_temporal_lagged --time-col=time --source-col=from --target-col=to --time-order=numeric --max-nodes=100 --max-transitions=2 --max-dyads=50000 --btergm=check --tergm=check --seed=20261013
	uv run python scripts/34_summarize_temporal_check.py --model-dir results/models/eu_core_temporal_lagged --panel-dir results/phase2/eu_core_temporal_check

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
