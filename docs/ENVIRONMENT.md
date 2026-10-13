# Reproducible environment

The project deliberately keeps Python and R separate. Python handles data engineering, directed graph and hypergraph operations, masking, LP/HP methods, and evaluation. R handles ERGM fitting and conditional simulation through `statnet`. Files exchanged between them use CSV plus a tracked metadata manifest; Parquet stays in the Python layer unless R Arrow is added later.

## Required local tools

| Tool | Version | Purpose |
|---|---:|---|
| Git | 2.40+ | Version control and GitHub synchronization |
| uv | 0.4+ | Python and virtual-environment management |
| Python | 3.11.x | Project runtime, installed by `uv` when needed |
| R | 4.4+ | ERGM/statnet estimation |
| GNU Make | optional | Shortcuts for setup and tests |

Python 3.11 is pinned in `.python-version`; the project supports Python 3.11 and 3.12. R packages are initialized from `r/bootstrap_renv.R`, which writes a machine-specific `renv.lock` once packages are installed.

## Python setup

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

Core Python dependencies are declared in `pyproject.toml` and locked in `uv.lock`. They cover numerical computing, tabular/columnar data, NetworkX, HyperNetX, low-rank baselines, plotting, configuration, and testing.

The neural stack is optional because PyTorch wheel selection depends on whether the computer uses CPU, CUDA, or Apple Silicon:

```bash
uv sync --extra dev --extra neural
```

Install NHP-D or DHGNN only after their upstream code and data-input requirements are verified during the benchmark pilot. They are not vendored into this repository.

## R/statnet setup

Install R 4.4+ first, then run:

```bash
Rscript r/bootstrap_renv.R
```

The bootstrap installs and locks:

- `network`, `ergm`, `sna`, and `statnet.common` for ERGM work;
- `data.table`, `jsonlite`, `yaml`, `digest`, and `optparse` for data interchange and scripts;
- `testthat` for R tests.

The valued-ERGM (`ergm.count`) and R Arrow packages are intentionally deferred until the relevant supplementary analysis requires them. They are not necessary for the data audit or the primary binary ERGM benchmark.

On Ubuntu/Debian, typical system prerequisites for source-installed R packages are:

```bash
sudo apt-get update
sudo apt-get install -y r-base r-base-dev libcurl4-openssl-dev libssl-dev libxml2-dev libfontconfig1-dev libharfbuzz-dev libfribidi-dev
```

On macOS, install R from CRAN and, if source compilation fails, install Xcode Command Line Tools. On Windows, install Rtools matching the installed R version. These operating-system packages are intentionally not committed to the project environment because they are platform-specific.

## Project conventions

- Raw and external data never enter Git. Store them under `data/raw/` or `data/external/`.
- Every analysis-ready dataset must have a provenance sheet before use.
- Use `configs/` for all parameters: seed, dataset, node-core policy, arity caps, masking regime, and evaluation panel.
- Python calls R through scripts and files, rather than `rpy2`, to keep the project portable.
- All generated results go under `results/`; manuscript-ready material is copied to `manuscript/` only through a scripted build step.

## Validation commands

```bash
make python
make r
make test
make lint
```

`make r` requires R to be installed. It is the only environment command that cannot be validated in a Python-only installation.
