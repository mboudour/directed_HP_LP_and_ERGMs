.DEFAULT_GOAL := help

.PHONY: help python neural r r-model-test test lint format clean phase2-status phase2-audits phase2-dry-run phase2-report phase2-enron-timestamps phase2-enron-primary phase2-enron-concepts phase2-enron-static phase2-enron-static-plan phase2-static phase2-export-masks phase2-eu-core-static-plan phase2-eu-core-score phase2-temporal-export phase2-eu-core-temporal phase2-eu-core-btergm phase2-eu-core-concepts

help:
	@printf '%s\n' \
	  'python  Install/synchronize the Python development environment.' \
	  'neural  Install/synchronize Python plus the optional PyTorch extra.' \
	  'r       Initialize the project-local R/statnet environment.' \
	  'r-model-test  Run dependency-free R contract tests for the ERGM/TERGM drivers.' \
	  'test    Run Python tests.' \
	  'lint    Run Ruff checks.' \
	  'format  Apply Ruff formatting.' \
	  'phase2-status  Report local data readiness and scientific gates.' \
	  'phase2-audits  Run all locally available, ungated Phase 2 source audits.' \
	  'phase2-dry-run  Show which Phase 2 source audits would run.' \
	  'phase2-report  Write one local report from completed audit metadata.' \
	  'phase2-enron-timestamps  Profile retained Enron event dates before selecting a study interval.' \
	  'phase2-enron-primary  Build the approved strict Enron custodian projection, core-100, and monthly panels.' \
	  'phase2-enron-concepts  Audit the cap-first Enron core-100 formal-concept section (|T|,|H| <= 3).' \
	  'phase2-enron-static  Run the fixed MCAR static arc-LP pilot on the validated Enron core-100.' \
	  'phase2-enron-static-plan  Fit the plan-aligned full-network Enron static ERGM ladder by MPLE.' \
	  'phase2-static  Run one static Phase 2 pilot; pass options in ARGS="...".' \
	  'phase2-export-masks  Export existing pilot masks; pass options in ARGS="...".' \
	  'phase2-eu-core-static-plan  Fit the plan-aligned EU-core static ERGM ladder.' \
	  'phase2-eu-core-score  Fit and score the plan-aligned EU-core masked ERGM ladder.' \
	  'phase2-eu-core-concepts  Audit the cap-first EU-core formal-concept section (|T|,|H| <= 3).' \
	  'phase2-temporal-export  Export a bounded chronological panel; pass options in ARGS="...".' \
	  'phase2-eu-core-temporal  Run the exploratory lagged-only EU-core baseline.' \
	  'phase2-eu-core-btergm  Install temporal R packages and run the planned bounded btergm ladder.' \
	  'clean   Remove local Python test and lint caches.'

python:
	uv sync --extra dev

neural:
	uv sync --extra dev --extra neural

r:
	Rscript r/bootstrap_renv.R

r-model-test:
	Rscript r/tests/test_model_drivers.R
	Rscript r/tests/test_temporal_btergm_ladder.R

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

phase2-enron-timestamps:
	uv run python scripts/14_profile_enron_event_timestamps.py --overwrite

phase2-enron-primary:
	uv run python scripts/15_materialize_enron_strict_mapping.py --overwrite
	uv run python scripts/25_build_enron_custodian_projection.py --overwrite

phase2-enron-concepts:
	uv run python scripts/28_audit_formal_concepts.py --dataset=enron_20150507 --edges=data/processed/enron_20150507/custodian_core100_static_arcs.parquet --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --source-col=tail_custodian --target-col=head_custodian --node-col=custodian_mailbox --output-dir=results/phase2/enron_formal_concepts_tail3_head3 --tail-cap=3 --head-cap=3 --max-candidates=250000 --overwrite

phase2-enron-static:
	uv run python scripts/30_run_static_benchmark.py --dataset=enron --mechanism=mcar --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --output-dir=results/phase2/enron_static_pilot --overwrite

phase2-enron-static-plan:
	Rscript r/models/static_directed_ergm_ladder.R --input=results/phase2/enron_static_pilot/r_inputs/static_edges.csv --nodes=results/phase2/enron_static_pilot/r_inputs/nodes.csv --output-dir=results/models/enron_static_ladder_plan --source-col=from --target-col=to --node-col=id --estimate=MPLE --degree-decay=0.5 --esp-decay=0.5 --seed=20261013 --overwrite=TRUE

phase2-static:
	uv run python scripts/30_run_static_benchmark.py $(ARGS)

phase2-export-masks:
	uv run python scripts/32_export_static_pilot_masks.py $(ARGS)

phase2-eu-core-static-plan:
	Rscript r/models/static_directed_ergm_ladder.R --input=results/phase2/eu_core_static_pilot/r_inputs/static_edges.csv --nodes=results/phase2/eu_core_static_pilot/r_inputs/nodes.csv --output-dir=results/models/eu_core_static_ladder_plan --source-col=from --target-col=to --node-col=id --estimate=MPLE --degree-decay=0.5 --esp-decay=0.5 --seed=20261013

phase2-eu-core-score: phase2-eu-core-static-plan
	Rscript r/models/score_masked_ergm.R --input-dir=results/phase2/eu_core_static_pilot --output-dir=results/models/eu_core_masked_ergm_plan --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013
	uv run python scripts/33_summarize_masked_ergm.py --input-dir results/models/eu_core_masked_ergm_plan

phase2-eu-core-concepts:
	uv run python scripts/28_audit_formal_concepts.py --dataset=email_eu_core_temporal --edges=data/processed/email_eu_core_temporal/core100_static_arcs.parquet --nodes=data/processed/email_eu_core_temporal/core100_nodes.csv --output-dir=results/phase2/eu_core_formal_concepts_tail3_head3 --tail-cap=3 --head-cap=3 --max-candidates=250000 --overwrite

phase2-temporal-export:
	uv run python scripts/31_export_temporal_panel.py $(ARGS)

phase2-eu-core-temporal:
	uv run python scripts/31_export_temporal_panel.py --dataset eu_core --panel-count 3 --output-dir results/phase2/eu_core_temporal_check
	Rscript r/models/temporal_lagged_check.R --input=results/phase2/eu_core_temporal_check/panel_edges.csv --nodes=results/phase2/eu_core_temporal_check/nodes.csv --output-dir=results/models/eu_core_temporal_lagged --time-col=time --source-col=from --target-col=to --time-order=numeric --max-nodes=100 --max-transitions=2 --max-dyads=50000 --btergm=check --tergm=check --seed=20261013
	uv run python scripts/34_summarize_temporal_check.py --model-dir results/models/eu_core_temporal_lagged --panel-dir results/phase2/eu_core_temporal_check

phase2-eu-core-btergm:
	$(MAKE) r
	$(MAKE) r-model-test
	Rscript r/models/temporal_btergm_ladder.R --input=results/phase2/eu_core_temporal_check/panel_edges.csv --nodes=results/phase2/eu_core_temporal_check/nodes.csv --output-dir=results/models/eu_core_temporal_btergm_v3 --bootstrap-reps=20 --degree-decay=0.5 --esp-decay=0.5 --models=all --parallel=no --ncpus=1 --seed=20261013 --overwrite=TRUE
	uv run python scripts/35_summarize_temporal_btergm.py --model-dir results/models/eu_core_temporal_btergm_v3 --panel-dir results/phase2/eu_core_temporal_check

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
