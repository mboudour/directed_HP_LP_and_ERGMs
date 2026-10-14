# Directed HP, LP, and ERGMs

A reproducible research repository for **directed link prediction (LP)**, **hyperlink prediction (HP)**, and **exponential random graph model (ERGM)** benchmarks under network missingness.

The project implements the research design in three phases:

1. **Data:** provenance audit, native-event construction, dyadic graph construction, and formal-concept hyperarcs.
2. **Computations:** masking regimes, directed LP/HP baselines, ERGM score lifts, diagnostics, and evaluation.
3. **Manuscript:** tables, figures, reproducible supplementary material, and paper sources.

## Environment

The repository uses two interoperable environments:

- **Python 3.11** managed by [`uv`](https://docs.astral.sh/uv/) for preparation, concept enumeration, masking, LP/HP, neural baselines, and evaluation.
- **R 4.4+** managed by [`renv`](https://rstudio.github.io/renv/) for `statnet`/ERGM estimation and conditional simulation.

Complete setup instructions and the dependency rationale are in [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md).

## Quick start

```bash
git clone https://github.com/mboudour/directed_HP_LP_and_ERGMs.git
cd directed_HP_LP_and_ERGMs
uv sync --extra dev
uv run pytest
Rscript r/bootstrap_renv.R
make phase2-status
```

The neural stack is intentionally optional because PyTorch installation depends on the local CPU/CUDA platform:

```bash
uv sync --extra dev --extra neural
```

## Repository layout

```text
.
├── configs/              # Reproducible experiment configurations
├── data/
│   ├── raw/              # Original files; never committed
│   ├── external/         # Downloaded source files; never committed
│   ├── interim/          # Intermediate derived artifacts; never committed
│   ├── processed/        # Analysis-ready data; never committed by default
│   └── metadata/         # Tracked provenance sheets and schemas
├── docs/                 # Environment and data-audit documentation
├── manuscript/           # Paper sections, tables, and figures
├── notebooks/            # Exploratory work only; final pipelines live in src/
├── r/                    # R/statnet scripts, models, and tests
├── results/              # Generated outputs; not committed by default
├── scripts/              # Thin command-line entry points
├── src/directed_hp/      # Python package
│   ├── data/             # Dataset adapters and validation
│   ├── graphs/           # Digraph construction and summaries
│   ├── hypergraphs/      # Native events and formal-concept hyperarcs
│   ├── masking/          # Event-first, arc-first, and footprint-free masks
│   ├── lp/               # Directed LP scores and factorization baselines
│   ├── ergm/             # R interchange and ERGM score integration
│   ├── evaluation/       # Candidates, negatives, metrics, and calibration
│   ├── models/           # Established HP-baseline wrappers
│   └── utils/            # Configuration, paths, seeds, and logging
└── tests/                # Python unit and integration tests
```

## Data policy

Do **not** commit raw email records, source archives, credentials, personal data, or generated files that cannot be redistributed. Every dataset must have a tracked provenance sheet in `docs/data_audits/` before it enters the computational pipeline.

## Current scope

The repository includes an audited Enron address-level provenance pipeline and a
manifest-driven Phase 2 preparation layer for Enron, EU-core, CAVIAR, Ciel, Jmail v1,
and MathOverflow. The canonical local workflow is described in
[docs/PHASE2_AUTOMATION.md](docs/PHASE2_AUTOMATION.md).

The bounded static computational pilot is documented in
[docs/STATIC_PILOT.md](docs/STATIC_PILOT.md). It provides a single reproducible entry
point for the initial directed LP, formal-concept fidelity, masking, and ERGM-input
checks while retaining the plan's scientific gates.

The paper's deliberately limited chronological component is documented in
[docs/BOUNDED_TEMPORAL_CHECK.md](docs/BOUNDED_TEMPORAL_CHECK.md). It keeps the full
TERGM/STERGM and relational-hyperevent forecasting study in the deferred second paper.

After placing the untracked source files in their registered `data/` locations, use:

```bash
make phase2-status
make phase2-dry-run
make phase2-audits
```

The batch runner executes only locally available, ungated audits. It does not silently
approve a provenance, direction, identity, or reconstruction policy gate.
