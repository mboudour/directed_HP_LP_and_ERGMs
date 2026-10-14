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
| M3 | `gwesp(..., type="OTP")` | Outgoing-two-path closure, matched to the OI LP component |
| M4 | M3 + `gwesp(..., type="OSP") + gwesp(..., type="ISP")` | Adds shared targets and shared sources, matched to OO and II |
| M4c | M4 + `ctriple` | Cyclic-closure sensitivity specification |

The exact directed shared-partner and triple terms are version dependent in `ergm`. The driver does not substitute another statistic: if a supplied `ergm` lacks a term or cannot estimate it, that model is recorded as `fit_failed` with its original formula and error. This is the meaning of “where available.”

Static outputs are `model_specs.csv`, `network_summary.csv`, `model_status.csv`, `coefficients.csv`, `diagnostics.txt`, `diagnostics.csv`, `model_objects.rds`, and `run_manifest.json`. `diagnostics.txt` captures `summary()` plus `mcmc.diagnostics()` for MCMLE fits; it explicitly says MCMC diagnostics are not applicable for MPLE.

## 2. Masked static-pilot conditional ERGM scoring

Use this driver only after a completed static pilot has exported its mask
contract with `scripts/32_export_static_pilot_masks.py`. It fits each selected
model independently to **each replicate's training edge list**, retaining the
full node universe so that isolates remain in the masked network.

```bash
Rscript r/models/score_masked_ergm.R \
  --input-dir=results/phase2/eu_core_static_pilot \
  --output-dir=results/models/eu_core_masked_ergm \
  --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013
```

The required layout beneath `--input-dir` is:

| Path | Required columns | Meaning |
|---|---|---|
| `r_inputs/nodes.csv` | `id` | Complete, unique node universe, including isolates. |
| `masks/replicate_001_train_edges.csv` (and later replicate IDs) | `from`, `to` | Directed edges observed for that replicate's ERGM fit. |
| `masks/replicate_001_candidates.csv` (same replicate IDs) | `candidate_tail`, `candidate_head`, `label` | Unique non-self candidate dyads and binary held-out labels (`0`/`1`). |

Every training-file prefix must have a matching candidate file. Candidate IDs
must occur in `nodes.csv`; duplicate candidates, self-loops, nonbinary labels,
and missing pair files are rejected. Actor IDs are treated as character labels,
so IDs such as `001` are not coerced to numeric values.

`--models` defaults to `M0,M1,M3,M4c` and accepts any unique comma-separated
subset of the static ladder labels. `--estimate` defaults to `MPLE` and may be
`MCMLE`; `--overwrite=TRUE` is required when reusing a non-empty output
directory. The driver requires `ergm` 4.12.0 or newer and records package
versions in its manifest.

For every successful masked fit, the scorer calls:

```r
predict(fit, conditional = TRUE, type = "response", output = "data.frame")
```

Statnet returns `tail` and `head` as node **indices** plus response-scale `p`.
The driver maps those indices through the ordered `nodes.csv$id` labels, then
selects only candidate dyads. It does not emit non-candidate dyads.

| Output | Contents |
|---|---|
| `conditional_predictions.csv` | Exactly `replicate`, `model`, `candidate_tail`, `candidate_head`, `label`, and `conditional_probability`; rows appear only for successfully fitted and scored model/replicate pairs. |
| `metrics.csv` | Per replicate/model accuracy, precision, recall, F1, Matthews correlation, ROC-AUC, PR-AUC, and log loss; every metric has a numeric value when defined and a visible status/message otherwise. Accuracy/precision/recall/F1/Matthews use a fixed conditional-probability threshold of 0.5. ROC-AUC uses average ranks (tie half-credit); PR-AUC is threshold-step average precision with score ties pooled; log loss is binary cross-entropy. |
| `replicate_status.csv` | Input/network status plus training, candidate, and label counts for each replicate. |
| `model_status.csv` | Per replicate/model formula, fit/prediction status, errors, warnings, and requested/predicted candidate counts. A failed model does not prevent later models or replicates from running. |
| `replicate_network_summary.csv` | Structural summary of each masked training network. |
| `run_manifest.json` | Paths, selected models, prediction method, package versions, counts, and limitations. |

If a candidate panel has no positives or no negatives, all metrics are written
as `NA` with status `not_defined_degenerate_labels`; this does not create an
artificial metric. Precision and Matthews correlation are also visibly `NA`
when a 0.5-threshold prediction contains only one class. A failed fit or
prediction gets its own visible status and `NA` metrics, rather than a
substituted model or score.

These are **exact conditional tie probabilities under the fitted ERGM and the
masked training network**. They are not unconditional probabilities, simulated
future ties, forecasts, or scores from a full-network fit. The driver reads no
raw data and never infers or opens a full pilot edge list.

## 3. Native-event ERGM conditional footprint scoring

`score_native_event_footprints.R` uses the same exact conditional-response
call as the masked arc scorer, but aggregates the fitted dyad probabilities
over predeclared tail/head candidate footprints. It requires the strict export
contract from `scripts/39_export_native_event_ergm_inputs.py`:

```bash
Rscript r/models/score_native_event_footprints.R \
  --input-dir=results/phase2/enron_native_event_ergm_inputs \
  --output-dir=results/models/enron_native_event_ergm_footprints \
  --models=M0,M1,M3,M4c --estimate=MPLE --seed=20261013 --overwrite=TRUE
```

For every frozen event-first split, the driver fits each selected model only to
the corresponding observed-projection `train_edges.csv`. It maps Statnet's
conditional probabilities to the exported candidate dyads and reports:

| Score | Definition | Scope |
|---|---|---|
| `L1` | Arithmetic mean of footprint dyad probabilities | Conditional graph-footprint support |
| `L1g` | Geometric mean of footprint dyad probabilities | Size-normalized conditional support |
| `L2` | Product of footprint dyad probabilities | Single-dyad conditional-pseudolikelihood ranking score |

Metrics use `log_L2`, a monotone numerically stable form of `L2`. The labels
remain recorded native event types, so the outputs report **ranking metrics
only**—ROC-AUC, PR-AUC, precision@k, recall@k. They do not report accuracy,
F1, MCC, log loss, or a probability that a native email event occurred. This
`L2` is not the plan's matched-marginal `L2` or joint ERGM simulation score
`L3-F`: it multiplies single-dyad conditional-pseudolikelihood scores.

The driver writes `event_footprint_scores.csv`, `ranking_metrics.csv`,
`metric_summary.csv`, `model_status.csv`, `split_status.csv`,
`network_summary.csv`, `summary.md`, and `run_manifest.json`. Failures remain
visible by split and model. See
[`docs/NATIVE_EVENT_ERGM_FOOTPRINTS.md`](../../docs/NATIVE_EVENT_ERGM_FOOTPRINTS.md)
for the native-event interpretation and Make target.

## 4. Conditional joint-footprint ERGM simulation

`simulate_joint_footprint_ergm.R` implements the plan's graph-footprint
completion score `L3-F` through candidate-specific conditional MCMC simulation.
It requires the same frozen native-event input export as the factorized ranking
pilot but has a different scientific role:

```bash
make phase2-enron-joint-footprints
```

For each bounded candidate, every observed split dyad remains fixed. Only that
candidate's footprint dyads not already present in the observed split
projection are marked missing, and Statnet simulates them under `constraints =
~observed`. From the same draws, it reports `L1`, `L1g`, the product of
candidate-specific marginals `L2`, the joint footprint-completion frequency
`L3-F`, and `log(L3-F)-log(L2)` where estimable.

The first run deliberately fits split-specific MCMLE `M1` and `M4` models but
limits eligibility to candidates with at most two unknown footprint dyads. It
samples at most five candidates per panel/label and uses 500 conditional draws
per candidate. It is a computational and dependence diagnostic—not a final
ranking evaluation, a native-event probability, or automatic MCMC/GOF approval.
See [`docs/JOINT_FOOTPRINT_SIMULATION.md`](../../docs/JOINT_FOOTPRINT_SIMULATION.md)
for the exact conditioning, zero-score handling, and output interpretation.

## 5. Exploratory lagged-only temporal baseline

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

For every ordered non-self dyad, the factorized conditional baseline models are:

\[
\begin{aligned}
L_0&:\ \operatorname{logit}\Pr(y_{ij,t}=1)=\beta_0,\\
L_1&:\ L_0+\beta_1 y_{ij,t-1},\\
L_{2,OO}&:\ L_1+\beta_2\operatorname{CN}^{out}_{ij,t-1},\\
\operatorname{CN}^{out}_{ij,t-1}&=\sum_k y_{ik,t-1}y_{jk,t-1}.
\end{aligned}
\]

Thus every right-hand-side network quantity is lagged. The output `factorized_coefficients.csv` is an exploratory GLM diagnostic; it is **not** the planned `T_tt`/`T0`–`T2` TERGM ladder, a jointly normalized temporal ERGM, a causal estimate, or a simulated forecast.

The driver always writes `proposition6_identity.csv`, a numerical toy-panel check of the Proposition 6 logistic ranking identity: for positive \(\beta\), `plogis(alpha + beta * CN)` has exactly the same strict ordering as the lagged common-neighbor count. It also verifies the one-unit common-neighbor odds multiplier is `exp(beta)`.

### `btergm` and `tergm` guardrails

Both options default to `check`, which writes `package_placeholder_status.csv`.

- `--btergm=check` confirms whether the package is installed without fitting. `--btergm=fit --btergm-reps=N` attempts the deliberately small `edges + mutual` bootstrap model over the bounded panel list. Its output, when it exists, is named `btergm_bootstrap_coefficients_not_forecasts.csv` and every row says **NOT a simulated forecast**.
- `--tergm=check` reports package availability and deliberately does not infer a `Form`/`Diss` model. `--tergm=fit` visibly fails after emitting its status row because an explicit formation/dissolution specification and a dynamic-network object are required; the edge-list CSV cannot supply those defensibly.
- Missing selected packages are recorded as `failure_missing_package`; requested `btergm=fit` also terminates nonzero rather than pretending to fit. A missing CSV or a violated input bound terminates nonzero with a failure manifest.

Temporal outputs are `factorized_model_specs.csv`, `factorized_model_status.csv`, `factorized_coefficients.csv`, `feature_summary.csv`, `proposition6_identity.csv`, `package_placeholder_status.csv`, RDS objects, and `temporal_manifest.json`.

## 6. Planned bounded temporal btergm ladder

`temporal_btergm_ladder.R` is a separate, portable implementation of the plan's
`T_tt`, `T0`, `T1`, `T2`, and `T2_minus_H` specifications. It requires explicit
`time,from,to` and `id` CSVs, validates at least two exact consecutive periods,
retains one fixed actor universe, and fits by **btergm MPLE/temporal bootstrap
only**. The default bootstrap replication count is 20 for a bounded pilot.

**T1/T2/T2_minus_H are MPLE conditional score estimators only, never forecasts;
no simulated probabilities are produced.** Temporal bootstrap is an estimator,
not a prediction competitor. This ladder is distinct from the exploratory
lagged-only GLMs above; its contemporaneous terms are not forecasting regressors.

See [`docs/TEMPORAL_BTERGM_LADDER.md`](../../docs/TEMPORAL_BTERGM_LADDER.md) for the
exact formulas, lagged OI/OO/II and degree matrices, btergm list-alignment contract,
CLI options, failure manifests, coefficient/interval artifacts, and base-R tests.

## Limitations

- The inputs must already encode the declared relation direction and binary tie rule. These drivers do not validate source provenance, address identity, or raw-message policies.
- ERGM sufficient statistics can be collinear or degenerate, especially in sparse/small directed networks. A successful call is not a guarantee of adequate goodness of fit; inspect the captured diagnostics and the model status/errors.
- The temporal GLMs factorize dyads conditional on lagged observations. They intentionally omit contemporaneous dependence and do not generate network trajectories.
- If no `--nodes` file is supplied, actors completely absent from the supplied edge list cannot be known or included.
