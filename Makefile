.DEFAULT_GOAL := help

.PHONY: help python neural r r-model-test test lint format clean phase2-status phase2-audits phase2-dry-run phase2-report phase2-publish-aggregate phase2-caviar-static-prep phase2-caviar-concepts phase2-caviar-concept-recovery phase2-caviar-static phase2-caviar-static-plan phase2-caviar-score phase2-ciel-audit phase2-jmail-audit phase2-mathoverflow-audit phase2-mathoverflow-profile phase2-mathoverflow-primary phase2-mathoverflow-static-prep phase2-mathoverflow-concepts phase2-mathoverflow-concept-recovery phase2-mathoverflow-native-fidelity phase2-mathoverflow-event-masks phase2-mathoverflow-native-heuristics phase2-mathoverflow-native-hard-panels phase2-mathoverflow-native-ergm-inputs phase2-mathoverflow-native-ergm-footprints phase2-mathoverflow-static phase2-mathoverflow-static-plan phase2-mathoverflow-score phase2-enron-timestamps phase2-enron-primary phase2-enron-mcmle-core50 phase2-enron-mcmle-core50-inputs phase2-enron-mcmle-core50-candidates phase2-enron-mcmle-core50-m2-gate phase2-enron-concepts phase2-enron-concept-recovery phase2-enron-native-fidelity phase2-enron-event-masks phase2-enron-native-heuristics phase2-enron-native-hard-panels phase2-enron-native-ergm-inputs phase2-enron-joint-footprints phase2-enron-joint-m4-mple-sensitivity phase2-enron-static phase2-enron-static-plan phase2-enron-score phase2-static phase2-export-masks phase2-eu-core-static-plan phase2-eu-core-score phase2-eu-core-concepts phase2-eu-core-concept-recovery phase2-temporal-export phase2-eu-core-temporal phase2-eu-core-btergm

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
	  'phase2-publish-aggregate  Collect non-sensitive aggregate output tables for the private repository.' \
	  'phase2-caviar-static-prep  Build the approved unique-labelled CAVIAR full static matrix.' \
	  'phase2-caviar-concepts  Audit CAVIAR full static formal concepts (|T|,|H| <= 3).' \
	  'phase2-caviar-concept-recovery  Evaluate CAVIAR arc-first formal-concept recovery.' \
	  'phase2-caviar-static  Run the fixed CAVIAR full static arc-LP pilot.' \
	  'phase2-caviar-static-plan  Fit the full-network CAVIAR static ERGM ladder by MPLE.' \
	  'phase2-caviar-score  Score CAVIAR frozen MCAR masks using conditional ERGM probabilities.' \
	  'phase2-ciel-audit  Audit Ciel matrix integrity without creating directed outputs.' \
	  'phase2-jmail-audit  Audit Jmail IDs, headers, and candidate events without building events.' \
	  'phase2-mathoverflow-audit  Audit MathOverflow posts without reconstructing events.' \
	  'phase2-mathoverflow-profile  Profile answer windows without reconstructing MathOverflow events.' \
	  'phase2-mathoverflow-primary  Build approved 30-day MathOverflow reconstructed events.' \
	  'phase2-mathoverflow-static-prep  Build MathOverflow static arcs and all-participant core-100 views.' \
	  'phase2-mathoverflow-concepts  Audit capped MathOverflow formal concepts (|T|,|H| <= 3).' \
	  'phase2-mathoverflow-concept-recovery  Evaluate MathOverflow arc-first formal-concept recovery.' \
	  'phase2-mathoverflow-native-fidelity  Compare reconstructed MathOverflow events with capped concepts.' \
	  'phase2-mathoverflow-event-masks  Create frozen MathOverflow event-type MCAR and MNAR-out masks.' \
	  'phase2-mathoverflow-native-heuristics  Score MathOverflow native events with lifted LP heuristics.' \
	  'phase2-mathoverflow-native-hard-panels  Score MathOverflow reversal and role-exchange panels.' \
	  'phase2-mathoverflow-native-ergm-footprints  Score MathOverflow native-event footprints by ERGM.' \
	  'phase2-mathoverflow-static  Run the fixed MathOverflow static arc-LP pilot.' \
	  'phase2-mathoverflow-static-plan  Fit the MathOverflow static ERGM ladder by MPLE.' \
	  'phase2-mathoverflow-score  Score MathOverflow frozen MCAR masks by ERGM conditional probabilities.' \
	  'phase2-enron-timestamps  Profile retained Enron event dates before selecting a study interval.' \
	  'phase2-enron-primary  Build the approved strict Enron custodian projection, core-100, and monthly panels.' \
	  'phase2-enron-mcmle-core50  Materialize the approved nested Enron core-50 for MCMLE feasibility only.' \
	  'phase2-enron-mcmle-core50-inputs  Build separate core-50 masks and joint-score candidate inputs.' \
	  'phase2-enron-mcmle-core50-candidates  Audit core-50 two-dyad candidate eligibility before MCMC.' \
	  'phase2-enron-mcmle-core50-m2-gate  Run the 120-second bounded core-50 M2 MCMLE feasibility gate.' \
	  'phase2-enron-concepts  Audit the cap-first Enron core-100 formal-concept section (|T|,|H| <= 3).' \
	  'phase2-enron-concept-recovery  Evaluate Enron arc-first formal-concept recovery.' \
	  'phase2-enron-native-fidelity  Compare strict Enron recorded events with the capped formal-concept section.' \
	  'phase2-enron-event-masks  Create three MCAR and three MNAR-out event-type masks for native-event evaluation.' \
	  'phase2-enron-native-heuristics  Score native event types with lifted LP heuristics on frozen event-first masks.' \
	  'phase2-enron-native-hard-panels  Score reversal and role-exchange negatives for directed native-event recovery.' \
	  'phase2-enron-native-ergm-inputs  Export frozen native-event panels for split-specific ERGM footprint scoring.' \
	  'phase2-enron-native-ergm-footprints  Fit masked ERGMs and score L1/L1g/L2 footprint completion on native-event panels.' \
	  'phase2-enron-joint-footprints  Run the one-split M1 conditional-simulation smoke test for L3-F.' \
	  'phase2-enron-joint-m4-mple-sensitivity  Run one bounded M4 MPLE parameter-plug-in sensitivity.' \
	  'phase2-enron-static  Run the fixed MCAR static arc-LP pilot on the validated Enron core-100.' \
	  'phase2-enron-static-plan  Fit the plan-aligned full-network Enron static ERGM ladder by MPLE.' \
	  'phase2-enron-score  Score frozen Enron MCAR masks with conditional probabilities from masked ERGMs.' \
	  'phase2-static  Run one static Phase 2 pilot; pass options in ARGS="...".' \
	  'phase2-export-masks  Export existing pilot masks; pass options in ARGS="...".' \
	  'phase2-eu-core-static-plan  Fit the plan-aligned EU-core static ERGM ladder.' \
	  'phase2-eu-core-score  Fit and score the plan-aligned EU-core masked ERGM ladder.' \
	  'phase2-eu-core-concepts  Audit the cap-first EU-core formal-concept section (|T|,|H| <= 3).' \
	  'phase2-eu-core-concept-recovery  Evaluate EU-core arc-first formal-concept recovery.' \
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
	Rscript r/tests/test_native_event_footprints.R
	Rscript r/tests/test_joint_footprint_simulation.R

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

phase2-publish-aggregate:
	uv run python scripts/45_collect_phase2_aggregate_outputs.py --overwrite

phase2-caviar-static-prep:
	uv run python scripts/22_prepare_covert_matrices.py caviar --scope=full_static --build-directed

phase2-caviar-concepts:
	uv run python scripts/28_audit_formal_concepts.py --dataset=caviar_full_static --edges=data/processed/caviar/directed_valued_arcs.parquet --nodes=data/processed/caviar/nodes.csv --source-col=tail --target-col=head --node-col=id --output-dir=results/phase2/caviar_full_static_formal_concepts_tail3_head3 --tail-cap=3 --head-cap=3 --max-candidates=250000 --overwrite
	@cat results/phase2/caviar_full_static_formal_concepts_tail3_head3/summary.md

phase2-caviar-concept-recovery: phase2-caviar-static-prep
	uv run python scripts/46_run_arcfirst_concept_recovery.py --dataset=caviar --mechanisms mcar mnar_out --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/caviar_concept_recovery --overwrite
	@cat results/phase2/caviar_concept_recovery/summary.md

phase2-caviar-static:
	uv run python scripts/30_run_static_benchmark.py --dataset=caviar --mechanism=mcar --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --output-dir=results/phase2/caviar_static_pilot --overwrite

phase2-caviar-static-plan:
	@test -f results/phase2/caviar_static_pilot/r_inputs/static_edges.csv || (echo 'STOP: run make phase2-caviar-static first.' && exit 1)
	Rscript r/models/static_directed_ergm_ladder.R --input=results/phase2/caviar_static_pilot/r_inputs/static_edges.csv --nodes=results/phase2/caviar_static_pilot/r_inputs/nodes.csv --output-dir=results/models/caviar_static_ladder_plan --source-col=from --target-col=to --node-col=id --estimate=MPLE --degree-decay=0.5 --esp-decay=0.5 --seed=20261013 --overwrite=TRUE
	@cat results/models/caviar_static_ladder_plan/model_status.csv

phase2-caviar-score:
	@test -f results/phase2/caviar_static_pilot/run_manifest.json || (echo 'STOP: run make phase2-caviar-static first.' && exit 1)
	uv run python scripts/32_export_static_pilot_masks.py --pilot-dir=results/phase2/caviar_static_pilot --overwrite
	Rscript r/models/score_masked_ergm.R --input-dir=results/phase2/caviar_static_pilot --output-dir=results/models/caviar_masked_ergm_plan --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013 --overwrite=TRUE
	uv run python scripts/33_summarize_masked_ergm.py --input-dir=results/models/caviar_masked_ergm_plan

phase2-ciel-audit:
	@if test -f data/metadata/ciel_matrix_preparation.json && test -f docs/data_audits/ciel_matrix_preparation.md; then \
		echo 'Ciel audit already exists; preserving the prior immutable audit record.'; \
		cat docs/data_audits/ciel_matrix_preparation.md; \
	elif test -e data/metadata/ciel_matrix_preparation.json || test -e docs/data_audits/ciel_matrix_preparation.md; then \
		echo 'STOP: inconsistent partial Ciel audit outputs; inspect them rather than overwriting.'; \
		exit 1; \
	else \
		uv run python scripts/22_prepare_covert_matrices.py ciel --scope=static; \
	fi

phase2-jmail-audit:
	@if test -f data/metadata/jmail_v1_2026_02_audit.json && test -f docs/data_audits/jmail_v1_2026_02_preparation.md; then \
		echo 'Jmail audit already exists; preserving the prior immutable audit record.'; \
		cat docs/data_audits/jmail_v1_2026_02_preparation.md; \
	elif test -e data/metadata/jmail_v1_2026_02_audit.json || test -e docs/data_audits/jmail_v1_2026_02_preparation.md; then \
		echo 'STOP: inconsistent partial Jmail audit outputs; inspect them rather than overwriting.'; \
		exit 1; \
	else \
		uv run python scripts/23_prepare_jmail_v1.py; \
	fi

phase2-mathoverflow-audit:
	@if test -f data/metadata/mathoverflow_stackexchange_2024_audit.json && test -f docs/data_audits/mathoverflow_stackexchange_2024_preparation.md; then \
		echo 'MathOverflow audit already exists; preserving the prior immutable audit record.'; \
		cat docs/data_audits/mathoverflow_stackexchange_2024_preparation.md; \
	elif test -e data/metadata/mathoverflow_stackexchange_2024_audit.json || test -e docs/data_audits/mathoverflow_stackexchange_2024_preparation.md; then \
		echo 'STOP: inconsistent partial MathOverflow audit outputs; inspect them rather than overwriting.'; \
		exit 1; \
	else \
		uv run python scripts/24_prepare_mathoverflow.py; \
	fi

phase2-mathoverflow-profile:
	@if test -f data/metadata/mathoverflow_reconstruction_profile.json && test -f docs/data_audits/mathoverflow_stackexchange_2024_reconstruction_profile.md; then \
		echo 'MathOverflow reconstruction profile already exists; preserving the prior immutable profile.'; \
		cat docs/data_audits/mathoverflow_stackexchange_2024_reconstruction_profile.md; \
	elif test -e data/metadata/mathoverflow_reconstruction_profile.json || test -e docs/data_audits/mathoverflow_stackexchange_2024_reconstruction_profile.md; then \
		 echo 'STOP: inconsistent partial MathOverflow profile outputs; inspect them rather than overwriting.'; \
		 exit 1; \
	else \
		uv run python scripts/43_profile_mathoverflow_reconstruction.py && \
		cat docs/data_audits/mathoverflow_stackexchange_2024_reconstruction_profile.md; \
	fi

phase2-mathoverflow-primary:
	@if test -f data/processed/mathoverflow_stackexchange_2024/native_events.parquet && test -f data/metadata/mathoverflow_stackexchange_2024_reconstruction.json && test -f docs/data_audits/mathoverflow_stackexchange_2024_reconstruction.md; then \
		echo 'MathOverflow primary reconstruction already exists; preserving the approved immutable build.'; \
		cat docs/data_audits/mathoverflow_stackexchange_2024_reconstruction.md; \
	elif test -e data/processed/mathoverflow_stackexchange_2024/native_events.parquet || test -e data/metadata/mathoverflow_stackexchange_2024_reconstruction.json || test -e docs/data_audits/mathoverflow_stackexchange_2024_reconstruction.md; then \
		echo 'STOP: inconsistent partial MathOverflow reconstruction outputs; inspect them rather than overwriting.'; \
		exit 1; \
	else \
		uv run python scripts/24_prepare_mathoverflow.py --build-reconstructed-events && \
		cat docs/data_audits/mathoverflow_stackexchange_2024_reconstruction.md; \
	fi

phase2-mathoverflow-static-prep:
	@if test -f data/processed/mathoverflow_stackexchange_2024/static_arcs.parquet && test -f data/processed/mathoverflow_stackexchange_2024/core100_static_arcs.parquet && test -f data/processed/mathoverflow_stackexchange_2024/core100_native_events.parquet && test -f data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv && test -f data/metadata/mathoverflow_stackexchange_2024_static_projection.json && test -f docs/data_audits/mathoverflow_stackexchange_2024_static_projection.md; then \
		echo 'MathOverflow static projection already exists; preserving the prior immutable build.'; \
		cat docs/data_audits/mathoverflow_stackexchange_2024_static_projection.md; \
	elif test -e data/processed/mathoverflow_stackexchange_2024/static_arcs.parquet || test -e data/processed/mathoverflow_stackexchange_2024/core100_static_arcs.parquet || test -e data/processed/mathoverflow_stackexchange_2024/core100_native_events.parquet || test -e data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv || test -e data/metadata/mathoverflow_stackexchange_2024_static_projection.json || test -e docs/data_audits/mathoverflow_stackexchange_2024_static_projection.md; then \
		echo 'STOP: inconsistent partial MathOverflow static-projection outputs; inspect them rather than overwriting.'; \
		exit 1; \
	else \
		uv run python scripts/44_prepare_mathoverflow_static_projection.py && \
		cat docs/data_audits/mathoverflow_stackexchange_2024_static_projection.md; \
	fi

phase2-mathoverflow-concepts: phase2-mathoverflow-static-prep
	uv run python scripts/28_audit_formal_concepts.py --dataset=mathoverflow_stackexchange_2024 --edges=data/processed/mathoverflow_stackexchange_2024/core100_static_arcs.parquet --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --source-col=tail --target-col=head --node-col=node --output-dir=results/phase2/mathoverflow_formal_concepts_tail3_head3 --tail-cap=3 --head-cap=3 --max-candidates=250000 --overwrite
	@cat results/phase2/mathoverflow_formal_concepts_tail3_head3/summary.md

phase2-mathoverflow-concept-recovery: phase2-mathoverflow-static-prep
	uv run python scripts/46_run_arcfirst_concept_recovery.py --dataset=mathoverflow --mechanisms mcar mnar_out --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/mathoverflow_concept_recovery --overwrite
	@cat results/phase2/mathoverflow_concept_recovery/summary.md

phase2-mathoverflow-native-fidelity: phase2-mathoverflow-static-prep
	uv run python scripts/29_audit_native_event_fidelity.py --dataset-id=mathoverflow_stackexchange_2024 --events=data/processed/mathoverflow_stackexchange_2024/core100_native_events.parquet --arcs=data/processed/mathoverflow_stackexchange_2024/core100_static_arcs.parquet --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --event-tail-column=tail_answerers --event-head-column=head_asker --arc-tail-column=tail --arc-head-column=head --node-column=node --tail-cap=3 --head-cap=3 --max-concept-candidates=250000 --output-dir=results/phase2/mathoverflow_native_event_fidelity_tail3_head3 --overwrite
	@cat results/phase2/mathoverflow_native_event_fidelity_tail3_head3/summary.md

phase2-mathoverflow-event-masks: phase2-mathoverflow-static-prep
	uv run python scripts/36_prepare_event_first_masks.py --dataset-id=mathoverflow_stackexchange_2024 --events=data/processed/mathoverflow_stackexchange_2024/core100_native_events.parquet --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --event-tail-column=tail_answerers --event-head-column=head_asker --node-column=node --tail-cap=3 --head-cap=3 --mask-rate=0.30 --mechanisms=mcar,mnar_out --replicates=30 --seed=20261013 --output-dir=results/phase2/mathoverflow_event_first_type_masks --overwrite
	@cat results/phase2/mathoverflow_event_first_type_masks/summary.md

phase2-mathoverflow-native-heuristics: phase2-mathoverflow-event-masks
	uv run python scripts/37_run_native_event_heuristics.py --dataset-id=mathoverflow_stackexchange_2024 --mask-dir=results/phase2/mathoverflow_event_first_type_masks --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --node-column=node --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/mathoverflow_event_first_native_heuristics --overwrite
	@cat results/phase2/mathoverflow_event_first_native_heuristics/summary.md

phase2-mathoverflow-native-hard-panels: phase2-mathoverflow-event-masks
	uv run python scripts/38_run_native_event_hard_panels.py --dataset-id=mathoverflow_stackexchange_2024 --mask-dir=results/phase2/mathoverflow_event_first_type_masks --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --node-column=node --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/mathoverflow_event_first_native_hard_panels --overwrite
	@cat results/phase2/mathoverflow_event_first_native_hard_panels/summary.md

phase2-mathoverflow-native-ergm-inputs: phase2-mathoverflow-native-heuristics phase2-mathoverflow-native-hard-panels
	uv run python scripts/39_export_native_event_ergm_inputs.py --dataset-id=mathoverflow_stackexchange_2024 --mask-dir=results/phase2/mathoverflow_event_first_type_masks --heuristic-dir=results/phase2/mathoverflow_event_first_native_heuristics --hard-panel-dir=results/phase2/mathoverflow_event_first_native_hard_panels --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --node-column=node --output-dir=results/phase2/mathoverflow_native_event_ergm_inputs --overwrite

phase2-mathoverflow-native-ergm-footprints: phase2-mathoverflow-native-ergm-inputs
	Rscript r/models/score_native_event_footprints.R --input-dir=results/phase2/mathoverflow_native_event_ergm_inputs --output-dir=results/models/mathoverflow_native_event_ergm_footprints --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013 --overwrite=TRUE
	@cat results/models/mathoverflow_native_event_ergm_footprints/summary.md

phase2-mathoverflow-static: phase2-mathoverflow-static-prep
	uv run python scripts/30_run_static_benchmark.py --dataset=mathoverflow --mechanism=mcar --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --output-dir=results/phase2/mathoverflow_static_pilot --overwrite

phase2-mathoverflow-static-plan: phase2-mathoverflow-static
	Rscript r/models/static_directed_ergm_ladder.R --input=results/phase2/mathoverflow_static_pilot/r_inputs/static_edges.csv --nodes=results/phase2/mathoverflow_static_pilot/r_inputs/nodes.csv --output-dir=results/models/mathoverflow_static_ladder_plan --source-col=from --target-col=to --node-col=id --estimate=MPLE --degree-decay=0.5 --esp-decay=0.5 --seed=20261013 --overwrite=TRUE

phase2-mathoverflow-score: phase2-mathoverflow-static
	uv run python scripts/32_export_static_pilot_masks.py --pilot-dir=results/phase2/mathoverflow_static_pilot --overwrite
	Rscript r/models/score_masked_ergm.R --input-dir=results/phase2/mathoverflow_static_pilot --output-dir=results/models/mathoverflow_masked_ergm_plan --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013 --overwrite=TRUE
	uv run python scripts/33_summarize_masked_ergm.py --input-dir=results/models/mathoverflow_masked_ergm_plan

phase2-enron-timestamps:
	uv run python scripts/14_profile_enron_event_timestamps.py --overwrite

phase2-enron-primary:
	uv run python scripts/15_materialize_enron_strict_mapping.py --overwrite
	uv run python scripts/25_build_enron_custodian_projection.py --overwrite

phase2-enron-mcmle-core50:
	uv run python scripts/41_materialize_enron_mcmle_core50.py --overwrite

phase2-enron-mcmle-core50-inputs: phase2-enron-mcmle-core50
	uv run python scripts/36_prepare_event_first_masks.py --dataset-id=enron_20150507_mcmle_core50 --events=data/processed/enron_20150507/custodian_mcmle_core50_native_events.parquet --nodes=data/processed/enron_20150507/custodian_mcmle_core50_nodes.csv --event-tail-column=tail_custodian --event-head-column=head_custodians --node-column=custodian_mailbox --tail-cap=3 --head-cap=3 --mask-rate=0.30 --mechanisms=mcar,mnar_out --replicates=3 --seed=20261013 --output-dir=results/phase2/enron_mcmle_core50_event_masks --overwrite
	uv run python scripts/37_run_native_event_heuristics.py --dataset-id=enron_20150507_mcmle_core50 --mask-dir=results/phase2/enron_mcmle_core50_event_masks --nodes=data/processed/enron_20150507/custodian_mcmle_core50_nodes.csv --node-column=custodian_mailbox --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/enron_mcmle_core50_native_heuristics --overwrite
	uv run python scripts/38_run_native_event_hard_panels.py --dataset-id=enron_20150507_mcmle_core50 --mask-dir=results/phase2/enron_mcmle_core50_event_masks --nodes=data/processed/enron_20150507/custodian_mcmle_core50_nodes.csv --node-column=custodian_mailbox --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/enron_mcmle_core50_native_hard_panels --overwrite
	uv run python scripts/39_export_native_event_ergm_inputs.py --dataset-id=enron_20150507_mcmle_core50 --mask-dir=results/phase2/enron_mcmle_core50_event_masks --heuristic-dir=results/phase2/enron_mcmle_core50_native_heuristics --hard-panel-dir=results/phase2/enron_mcmle_core50_native_hard_panels --nodes=data/processed/enron_20150507/custodian_mcmle_core50_nodes.csv --node-column=custodian_mailbox --output-dir=results/phase2/enron_mcmle_core50_joint_inputs --overwrite
	@cat results/phase2/enron_mcmle_core50_joint_inputs/manifest.json

phase2-enron-mcmle-core50-candidates:
	@test -f results/phase2/enron_mcmle_core50_joint_inputs/manifest.json || (echo 'STOP: run make phase2-enron-mcmle-core50-inputs first.' && exit 1)
	uv run python scripts/42_audit_joint_candidate_eligibility.py --dataset-id=enron_20150507_mcmle_core50 --input-dir=results/phase2/enron_mcmle_core50_joint_inputs --output-dir=results/phase2/enron_mcmle_core50_joint_candidate_eligibility --overwrite
	@cat results/phase2/enron_mcmle_core50_joint_candidate_eligibility/summary.md
	@cat results/phase2/enron_mcmle_core50_joint_candidate_eligibility/split_selection_summary.csv

phase2-enron-mcmle-core50-m2-gate:
	@test -f results/phase2/enron_mcmle_core50_joint_inputs/manifest.json || (echo 'STOP: run make phase2-enron-mcmle-core50-inputs first.' && exit 1)
	@set +e; \
	python3 scripts/40_run_bounded_command.py --timeout-seconds=120 --log=results/models/enron_mcmle_core50_m2_gate_run.txt -- Rscript r/models/simulate_joint_footprint_ergm.R --input-dir=results/phase2/enron_mcmle_core50_joint_inputs --output-dir=results/models/enron_mcmle_core50_m2_gate --models=M2 --estimate=MCMLE --split=mcar_replicate_002 --max-candidates-per-label=1 --min-unobserved-dyads=2 --max-unobserved-dyads=2 --require-reverse-observed=TRUE --nsim=200 --mcmc-burnin=100 --mcmc-interval=10 --fit-mcmc-burnin=1000 --fit-mcmc-interval=100 --fit-mcmc-samplesize=256 --mcmle-maxit=5 --bootstrap-reps=1000 --seed=20261013 --overwrite=TRUE; \
	run_status=$$?; \
	echo "===== bounded core-50 M2 runner exit code: $$run_status ====="; \
	cat results/models/enron_mcmle_core50_m2_gate_run.txt; \
	if [ -f results/models/enron_mcmle_core50_m2_gate/summary.md ]; then cat results/models/enron_mcmle_core50_m2_gate/summary.md; fi; \
	if [ -f results/models/enron_mcmle_core50_m2_gate/model_status.csv ]; then cat results/models/enron_mcmle_core50_m2_gate/model_status.csv; fi; \
	exit $$run_status

phase2-enron-concepts:
	uv run python scripts/28_audit_formal_concepts.py --dataset=enron_20150507 --edges=data/processed/enron_20150507/custodian_core100_static_arcs.parquet --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --source-col=tail_custodian --target-col=head_custodian --node-col=custodian_mailbox --output-dir=results/phase2/enron_formal_concepts_tail3_head3 --tail-cap=3 --head-cap=3 --max-candidates=250000 --overwrite

phase2-enron-concept-recovery: phase2-enron-primary
	uv run python scripts/46_run_arcfirst_concept_recovery.py --dataset=enron --mechanisms mcar mnar_out --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/enron_concept_recovery --overwrite
	@cat results/phase2/enron_concept_recovery/summary.md

phase2-enron-native-fidelity:
	uv run python scripts/29_audit_native_event_fidelity.py --dataset-id=enron_20150507 --events=data/processed/enron_20150507/custodian_native_events.parquet --arcs=data/processed/enron_20150507/custodian_core100_static_arcs.parquet --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --event-tail-column=tail_custodian --event-head-column=head_custodians --arc-tail-column=tail_custodian --arc-head-column=head_custodian --node-column=custodian_mailbox --tail-cap=3 --head-cap=3 --max-concept-candidates=250000 --output-dir=results/phase2/enron_native_event_fidelity_tail3_head3 --overwrite
	@cat results/phase2/enron_native_event_fidelity_tail3_head3/summary.md

phase2-enron-event-masks:
	uv run python scripts/36_prepare_event_first_masks.py --dataset-id=enron_20150507 --events=data/processed/enron_20150507/custodian_native_events.parquet --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --event-tail-column=tail_custodian --event-head-column=head_custodians --node-column=custodian_mailbox --tail-cap=3 --head-cap=3 --mask-rate=0.30 --mechanisms=mcar,mnar_out --replicates=30 --seed=20261013 --output-dir=results/phase2/enron_event_first_type_masks --overwrite
	@cat results/phase2/enron_event_first_type_masks/summary.md

phase2-enron-native-heuristics: phase2-enron-event-masks
	uv run python scripts/37_run_native_event_heuristics.py --dataset-id=enron_20150507 --mask-dir=results/phase2/enron_event_first_type_masks --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --node-column=custodian_mailbox --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/enron_event_first_native_heuristics --overwrite
	@cat results/phase2/enron_event_first_native_heuristics/summary.md

phase2-enron-native-hard-panels: phase2-enron-event-masks
	uv run python scripts/38_run_native_event_hard_panels.py --dataset-id=enron_20150507 --mask-dir=results/phase2/enron_event_first_type_masks --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --node-column=custodian_mailbox --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/enron_event_first_native_hard_panels --overwrite
	@cat results/phase2/enron_event_first_native_hard_panels/summary.md

phase2-enron-native-ergm-inputs: phase2-enron-native-heuristics phase2-enron-native-hard-panels
	uv run python scripts/39_export_native_event_ergm_inputs.py --dataset-id=enron_20150507 --mask-dir=results/phase2/enron_event_first_type_masks --heuristic-dir=results/phase2/enron_event_first_native_heuristics --hard-panel-dir=results/phase2/enron_event_first_native_hard_panels --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --node-column=custodian_mailbox --output-dir=results/phase2/enron_native_event_ergm_inputs --overwrite

phase2-enron-native-ergm-footprints: phase2-enron-native-ergm-inputs
	Rscript r/models/score_native_event_footprints.R --input-dir=results/phase2/enron_native_event_ergm_inputs --output-dir=results/models/enron_native_event_ergm_footprints --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013 --overwrite=TRUE
	@cat results/models/enron_native_event_ergm_footprints/summary.md

phase2-enron-joint-footprints: phase2-enron-native-ergm-inputs
	Rscript r/models/simulate_joint_footprint_ergm.R --input-dir=results/phase2/enron_native_event_ergm_inputs --output-dir=results/models/enron_joint_footprint_mcmle_smoke --models=M1 --split=mcar_replicate_001 --max-candidates-per-label=1 --min-unobserved-dyads=2 --max-unobserved-dyads=2 --require-reverse-observed=TRUE --nsim=200 --mcmc-burnin=500 --mcmc-interval=50 --fit-mcmc-burnin=1000 --fit-mcmc-interval=100 --fit-mcmc-samplesize=256 --mcmle-maxit=5 --bootstrap-reps=1000 --seed=20261013 --overwrite=TRUE
	@cat results/models/enron_joint_footprint_mcmle_smoke/summary.md

phase2-enron-joint-m4-mple-sensitivity: phase2-enron-native-ergm-inputs
	Rscript r/models/simulate_joint_footprint_ergm.R --input-dir=results/phase2/enron_native_event_ergm_inputs --output-dir=results/models/enron_joint_footprint_m4_mple_sensitivity --models=M4 --estimate=MPLE --split=mcar_replicate_001 --max-candidates-per-label=1 --min-unobserved-dyads=2 --max-unobserved-dyads=2 --require-reverse-observed=TRUE --nsim=200 --mcmc-burnin=100 --mcmc-interval=10 --bootstrap-reps=1000 --seed=20261013 --overwrite=TRUE
	@cat results/models/enron_joint_footprint_m4_mple_sensitivity/summary.md

phase2-enron-static:
	uv run python scripts/30_run_static_benchmark.py --dataset=enron --mechanism=mcar --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --output-dir=results/phase2/enron_static_pilot --overwrite

phase2-enron-static-plan:
	Rscript r/models/static_directed_ergm_ladder.R --input=results/phase2/enron_static_pilot/r_inputs/static_edges.csv --nodes=results/phase2/enron_static_pilot/r_inputs/nodes.csv --output-dir=results/models/enron_static_ladder_plan --source-col=from --target-col=to --node-col=id --estimate=MPLE --degree-decay=0.5 --esp-decay=0.5 --seed=20261013 --overwrite=TRUE

phase2-enron-score:
	uv run python scripts/32_export_static_pilot_masks.py --pilot-dir=results/phase2/enron_static_pilot --overwrite
	Rscript r/models/score_masked_ergm.R --input-dir=results/phase2/enron_static_pilot --output-dir=results/models/enron_masked_ergm_plan --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013 --overwrite=TRUE
	uv run python scripts/33_summarize_masked_ergm.py --input-dir=results/models/enron_masked_ergm_plan

phase2-static:
	uv run python scripts/30_run_static_benchmark.py $(ARGS)

phase2-export-masks:
	uv run python scripts/32_export_static_pilot_masks.py $(ARGS)

phase2-eu-core-static-plan:
	Rscript r/models/static_directed_ergm_ladder.R --input=results/phase2/eu_core_static_pilot/r_inputs/static_edges.csv --nodes=results/phase2/eu_core_static_pilot/r_inputs/nodes.csv --output-dir=results/models/eu_core_static_ladder_plan --source-col=from --target-col=to --node-col=id --estimate=MPLE --degree-decay=0.5 --esp-decay=0.5 --seed=20261013 --overwrite=TRUE

phase2-eu-core-score: phase2-eu-core-static-plan
	uv run python scripts/32_export_static_pilot_masks.py --pilot-dir=results/phase2/eu_core_static_pilot --overwrite
	Rscript r/models/score_masked_ergm.R --input-dir=results/phase2/eu_core_static_pilot --output-dir=results/models/eu_core_masked_ergm_plan --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013 --overwrite=TRUE
	uv run python scripts/33_summarize_masked_ergm.py --input-dir results/models/eu_core_masked_ergm_plan

phase2-eu-core-concepts:
	uv run python scripts/28_audit_formal_concepts.py --dataset=email_eu_core_temporal --edges=data/processed/email_eu_core_temporal/core100_static_arcs.parquet --nodes=data/processed/email_eu_core_temporal/core100_nodes.csv --output-dir=results/phase2/eu_core_formal_concepts_tail3_head3 --tail-cap=3 --head-cap=3 --max-candidates=250000 --overwrite

phase2-eu-core-concept-recovery:
	uv run python scripts/46_run_arcfirst_concept_recovery.py --dataset=eu_core --mechanisms mcar mnar_out --replicates=3 --mask-rate=0.30 --tail-cap=3 --head-cap=3 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/eu_core_concept_recovery --overwrite
	@cat results/phase2/eu_core_concept_recovery/summary.md

phase2-temporal-export:
	uv run python scripts/31_export_temporal_panel.py $(ARGS)

phase2-eu-core-temporal:
	uv run python scripts/31_export_temporal_panel.py --dataset eu_core --panel-count 3 --output-dir results/phase2/eu_core_temporal_check --overwrite
	Rscript r/models/temporal_lagged_check.R --input=results/phase2/eu_core_temporal_check/panel_edges.csv --nodes=results/phase2/eu_core_temporal_check/nodes.csv --output-dir=results/models/eu_core_temporal_lagged --time-col=time --source-col=from --target-col=to --time-order=numeric --max-nodes=100 --max-transitions=2 --max-dyads=50000 --btergm=check --tergm=check --seed=20261013 --overwrite=TRUE
	uv run python scripts/34_summarize_temporal_check.py --model-dir results/models/eu_core_temporal_lagged --panel-dir results/phase2/eu_core_temporal_check

phase2-eu-core-btergm:
	$(MAKE) r
	$(MAKE) r-model-test
	Rscript r/models/temporal_btergm_ladder.R --input=results/phase2/eu_core_temporal_check/panel_edges.csv --nodes=results/phase2/eu_core_temporal_check/nodes.csv --output-dir=results/models/eu_core_temporal_btergm_v3 --bootstrap-reps=20 --degree-decay=0.5 --esp-decay=0.5 --models=all --parallel=no --ncpus=1 --seed=20261013 --overwrite=TRUE
	uv run python scripts/35_summarize_temporal_btergm.py --model-dir results/models/eu_core_temporal_btergm_v3 --panel-dir results/phase2/eu_core_temporal_check

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov

.PHONY: phase2-enron-fidelity-rewire
phase2-enron-fidelity-rewire:
	uv run python scripts/47_degree_preserving_fidelity_null.py --dataset-id=enron_20150507 --events=data/processed/enron_20150507/custodian_native_events.parquet --arcs=data/processed/enron_20150507/custodian_core100_static_arcs.parquet --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --event-tail-column=tail_custodian --event-head-column=head_custodians --arc-tail-column=tail_custodian --arc-head-column=head_custodian --node-column=custodian_mailbox --tail-cap=3 --head-cap=3 --max-concept-candidates=250000 --rewires=100 --swaps-per-arc=10 --max-attempts-per-swap=100 --seed=20261013 --output-dir=results/phase2/enron_fidelity_rewire_null --overwrite
	@cat results/phase2/enron_fidelity_rewire_null/summary.md

.PHONY: phase2-enron-footprint-free phase2-eu-core-footprint-free phase2-caviar-footprint-free phase2-mathoverflow-footprint-free
phase2-enron-footprint-free:
	uv run python scripts/48_run_footprint_free_stress.py --dataset=enron --replicates=3 --target-fraction=0.30 --tail-cap=3 --head-cap=3 --max-concept-candidates=250000 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/enron_footprint_free_stress --overwrite
	@cat results/phase2/enron_footprint_free_stress/summary.md

phase2-eu-core-footprint-free:
	uv run python scripts/48_run_footprint_free_stress.py --dataset=eu_core --replicates=3 --target-fraction=0.30 --tail-cap=3 --head-cap=3 --max-concept-candidates=250000 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/eu_core_footprint_free_stress --overwrite
	@cat results/phase2/eu_core_footprint_free_stress/summary.md

phase2-caviar-footprint-free:
	uv run python scripts/48_run_footprint_free_stress.py --dataset=caviar --replicates=3 --target-fraction=0.30 --tail-cap=3 --head-cap=3 --max-concept-candidates=250000 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/caviar_footprint_free_stress --overwrite
	@cat results/phase2/caviar_footprint_free_stress/summary.md

phase2-mathoverflow-footprint-free:
	uv run python scripts/48_run_footprint_free_stress.py --dataset=mathoverflow --replicates=3 --target-fraction=0.30 --tail-cap=3 --head-cap=3 --max-concept-candidates=250000 --max-weak-distance=2 --seed=20261013 --output-dir=results/phase2/mathoverflow_footprint_free_stress --overwrite
	@cat results/phase2/mathoverflow_footprint_free_stress/summary.md

.PHONY: phase2-enron-role-assignment phase2-mathoverflow-role-assignment
phase2-enron-role-assignment:
	uv run python scripts/49_evaluate_native_event_role_assignment.py --dataset-id=enron_20150507 --mask-dir=results/phase2/enron_event_first_type_masks --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --node-column=custodian_mailbox --seed=20261013 --output-dir=results/phase2/enron_native_event_role_assignment --overwrite
	@cat results/phase2/enron_native_event_role_assignment/summary.md

phase2-mathoverflow-role-assignment:
	uv run python scripts/49_evaluate_native_event_role_assignment.py --dataset-id=mathoverflow_stackexchange_2024 --mask-dir=results/phase2/mathoverflow_event_first_type_masks --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --node-column=node --seed=20261013 --output-dir=results/phase2/mathoverflow_native_event_role_assignment --overwrite
	@cat results/phase2/mathoverflow_native_event_role_assignment/summary.md

.PHONY: phase2-enron-native-sensitivity phase2-mathoverflow-native-sensitivity
phase2-enron-native-sensitivity:
	uv run python scripts/50_run_native_missingness_sensitivity.py --dataset-id=enron_20150507 --events=data/processed/enron_20150507/custodian_native_events.parquet --nodes=data/processed/enron_20150507/custodian_core100_nodes.csv --event-tail-column=tail_custodian --event-head-column=head_custodians --node-column=custodian_mailbox --rates=0.10,0.20,0.50 --mechanisms=mcar,mnar_out,mnar_in --replicates=3 --tail-cap=3 --head-cap=3 --max-weak-distance=2 --seed=20261013 --output-root=results/phase2/enron_native_missingness_sensitivity_raw --overwrite
	uv run python scripts/51_summarize_native_missingness_sensitivity.py --dataset-id=enron_20150507 --input-root=results/phase2/enron_native_missingness_sensitivity_raw --output-dir=results/phase2/enron_native_missingness_sensitivity --overwrite
	@cat results/phase2/enron_native_missingness_sensitivity/summary.md

phase2-mathoverflow-native-sensitivity:
	uv run python scripts/50_run_native_missingness_sensitivity.py --dataset-id=mathoverflow_stackexchange_2024 --events=data/processed/mathoverflow_stackexchange_2024/core100_native_events.parquet --nodes=data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv --event-tail-column=tail_answerers --event-head-column=head_asker --node-column=node --rates=0.10,0.20,0.50 --mechanisms=mcar,mnar_out,mnar_in --replicates=3 --tail-cap=3 --head-cap=3 --max-weak-distance=2 --seed=20261013 --output-root=results/phase2/mathoverflow_native_missingness_sensitivity_raw --overwrite
	uv run python scripts/51_summarize_native_missingness_sensitivity.py --dataset-id=mathoverflow_stackexchange_2024 --input-root=results/phase2/mathoverflow_native_missingness_sensitivity_raw --output-dir=results/phase2/mathoverflow_native_missingness_sensitivity --overwrite
	@cat results/phase2/mathoverflow_native_missingness_sensitivity/summary.md

.PHONY: phase2-enron-paired-uncertainty phase2-mathoverflow-paired-uncertainty
phase2-enron-paired-uncertainty: phase2-enron-native-ergm-footprints
	uv run python scripts/52_paired_mask_uncertainty.py --dataset-id=enron_20150507 --kind=native_heuristic --input-dir=results/phase2/enron_event_first_native_heuristics --output-dir=results/phase2/enron_native_heuristic_paired_uncertainty --bootstrap-reps=10000 --permutation-reps=20000 --seed=20261013 --overwrite
	uv run python scripts/52_paired_mask_uncertainty.py --dataset-id=enron_20150507 --kind=native_ergm --input-dir=results/models/enron_native_event_ergm_footprints --output-dir=results/models/enron_native_ergm_paired_uncertainty --bootstrap-reps=10000 --permutation-reps=20000 --seed=20261013 --overwrite
	@cat results/phase2/enron_native_heuristic_paired_uncertainty/summary.md
	@cat results/models/enron_native_ergm_paired_uncertainty/summary.md

phase2-mathoverflow-paired-uncertainty: phase2-mathoverflow-native-ergm-footprints
	uv run python scripts/52_paired_mask_uncertainty.py --dataset-id=mathoverflow_stackexchange_2024 --kind=native_heuristic --input-dir=results/phase2/mathoverflow_event_first_native_heuristics --output-dir=results/phase2/mathoverflow_native_heuristic_paired_uncertainty --bootstrap-reps=10000 --permutation-reps=20000 --seed=20261013 --overwrite
	uv run python scripts/52_paired_mask_uncertainty.py --dataset-id=mathoverflow_stackexchange_2024 --kind=native_ergm --input-dir=results/models/mathoverflow_native_event_ergm_footprints --output-dir=results/models/mathoverflow_native_ergm_paired_uncertainty --bootstrap-reps=10000 --permutation-reps=20000 --seed=20261013 --overwrite
	@cat results/phase2/mathoverflow_native_heuristic_paired_uncertainty/summary.md
	@cat results/models/mathoverflow_native_ergm_paired_uncertainty/summary.md
