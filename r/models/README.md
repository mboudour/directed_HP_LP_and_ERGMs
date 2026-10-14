# Portable directed ERGM drivers

These are **R 4.4+ command-line drivers** for already prepared, binary directed data. They do not inspect `data/raw/`, infer dataset-specific direction semantics, choose a core, or reconstruct a temporal panel. All paths are explicit and recorded in a JSON manifest.

Run `Rscript r/bootstrap_renv.R` once in a project checkout to install the recommended `statnet`, `tergm`, `btergm`, `jsonlite`, and supporting packages. The drivers print a machine-readable contract with `--help` and may be invoked from any working directory.

## 1. Static directed ERGM ladder

```bash
Rscript r/models/static_directed_ergm_ladder.R \
  --input=data/processed/my_dataset/static_edges.csv \
  --nodes=data/processed/my_dataset/nodes.csv \
  --output-dir=results/models/my_dataset/static_ladder \
  --source-col=from --target-col=to --node-col=id \
  --estimate=MPLE
```

### Static input contract

`--input` is a CSV with one binary directed tie per row. By default the endpoint headers are `from` and `to`; select different headers using `--source-col` and `--target-col`. Duplicate rows are collapsed and self-loops are dropped by default (or rejected with `--drop-loops=FALSE`). Edge weights are deliberately not interpreted.

`--nodes` is optional but recommended. It is a CSV containing the full actor universe in one unique, nonempty ID column (default `id`). It preserves isolates and prevents a model from silently treating the observed endpoints as the complete network. Every endpoint in the edge list must occur in this file.

### Ladder specification

All decay parameters are fixed and recorded, avoiding an unbounded curved-term search. The driver attempts every specification and writes a row to `model_status.csv`; term support and numerical failures are never silently dropped.

| Model | Terms beyond prior specification | Purpose |
|---|---|---|
| M0 | `edges` | Directed density baseline |
| M1 | `mutual` | Reciprocal ties |
| M2 | `gwodegree`, `gwidegree` | Sender/receiver degree heterogeneity |
| M3a | `gwesp(..., type="OTP")` | Outgoing-two-path directed edgewise shared partners |
| M3b | `gwesp(..., type="ITP")` | Incoming-two-path directed edgewise shared partners |
| M3c | `gwesp(..., type="RTP")` | Reciprocated-two-path directed edgewise shared partners |
| M4a | M3a + `ttriple` | Directed transitive triples |
| M4b | M3a + `ctriple` | Directed cyclic triples |
| M4c | M3a + `ttriple + ctriple` | Joint transitive/cyclic specification |

The exact directed shared-partner and triple terms are version dependent in `ergm`. The driver does not substitute another statistic: if a supplied `ergm` lacks a term or cannot estimate it, that model is recorded as `fit_failed` with its original formula and error. This is the meaning of “where available.”

Static outputs are `model_specs.csv`, `network_summary.csv`, `model_status.csv`, `coefficients.csv`, `diagnostics.txt`, `diagnostics.csv`, `model_objects.rds`, and `run_manifest.json`. `diagnostics.txt` captures `summary()` plus `mcmc.diagnostics()` for MCMLE fits; it explicitly says MCMC diagnostics are not applicable for MPLE.

## 2. Bounded temporal lagged-only check

```bash
Rscript r/models/temporal_lagged_check.R \
  --input=data/processed/my_dataset/monthly_edges.csv \
  --nodes=data/processed/my_dataset/nodes.csv \
  --output-dir=results/models/my_dataset/temporal_check \
  --time-col=month --source-col=from --target-col=to \
  --max-nodes=100 --max-transitions=2 --max-dyads=50000
```

The panel CSV has one binary directed tie per row and requires time, source, and target columns. Time is sorted lexically by default (appropriate for zero-padded ISO dates such as `2025-01`); use `--time-order=numeric` only for numeric periods. The same optional node-universe contract applies. Missing ties in a listed period are treated as zeros **only for the explicitly supplied actor universe and panel times**.

The check is bounded: it rejects rather than silently subsets an input exceeding `--max-nodes`, `--max-transitions`, or `--max-dyads`. Defaults are 100 nodes, two adjacent transitions, and 50,000 dyad-time rows.

For every ordered non-self dyad, the factorized conditional models are:

\[
\begin{aligned}
T_{tt}&=y_{ij,t},\\
T_0&:\ \operatorname{logit}\Pr(y_{ij,t}=1)=\beta_0,\\
T_1&:\ T_0+\beta_1 y_{ij,t-1},\\
T_2&:\ T_1+\beta_2\operatorname{CN}^{out}_{ij,t-1},\\
\operatorname{CN}^{out}_{ij,t-1}&=\sum_k y_{ik,t-1}y_{jk,t-1}.
\end{aligned}
\]

Thus every right-hand-side network quantity is lagged. The output `factorized_coefficients.csv` is a GLM diagnostic; it is **not** a jointly normalized temporal ERGM, a causal estimate, or a simulated forecast.

The driver always writes `proposition6_identity.csv`, a numerical toy-panel check of the Proposition 6 logistic ranking identity: for positive \(\beta\), `plogis(alpha + beta * CN)` has exactly the same strict ordering as the lagged common-neighbor count. It also verifies the one-unit common-neighbor odds multiplier is `exp(beta)`.

### `btergm` and `tergm` guardrails

Both options default to `check`, which writes `package_placeholder_status.csv`.

- `--btergm=check` confirms whether the package is installed without fitting. `--btergm=fit --btergm-reps=N` attempts the deliberately small `edges + mutual` bootstrap model over the bounded panel list. Its output, when it exists, is named `btergm_bootstrap_coefficients_not_forecasts.csv` and every row says **NOT a simulated forecast**.
- `--tergm=check` reports package availability and deliberately does not infer a `Form`/`Diss` model. `--tergm=fit` visibly fails after emitting its status row because an explicit formation/dissolution specification and a dynamic-network object are required; the edge-list CSV cannot supply those defensibly.
- Missing selected packages are recorded as `failure_missing_package`; requested `btergm=fit` also terminates nonzero rather than pretending to fit. A missing CSV or a violated input bound terminates nonzero with a failure manifest.

Temporal outputs are `factorized_model_specs.csv`, `factorized_model_status.csv`, `factorized_coefficients.csv`, `feature_summary.csv`, `proposition6_identity.csv`, `package_placeholder_status.csv`, RDS objects, and `temporal_manifest.json`.

## Limitations

- The inputs must already encode the declared relation direction and binary tie rule. These drivers do not validate source provenance, address identity, or raw-message policies.
- ERGM sufficient statistics can be collinear or degenerate, especially in sparse/small directed networks. A successful call is not a guarantee of adequate goodness of fit; inspect the captured diagnostics and the model status/errors.
- The temporal GLMs factorize dyads conditional on lagged observations. They intentionally omit contemporaneous dependence and do not generate network trajectories.
- If no `--nodes` file is supplied, actors completely absent from the supplied edge list cannot be known or included.
