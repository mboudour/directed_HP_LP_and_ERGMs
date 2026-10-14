# Bounded temporal btergm ladder

`r/models/temporal_btergm_ladder.R` implements the plan's **T_tt, T0, T1, T2, and T2_minus_H** specifications on an explicitly exported directed panel. It estimates all selected models using **btergm MPLE with temporal bootstrap only**. It does not forecast, simulate probabilities, use MCMC-MLE, or infer a formation/dissolution model.

**T1, T2, and T2_minus_H are MPLE conditional score estimators only, never forecasts.** They include contemporaneous network dependence; fitted coefficients must not be interpreted as lagged-only future-tie probabilities. The temporal bootstrap is the estimator and uncertainty procedure, **not a separate prediction competitor**. No prediction or simulated-probability file is produced.

## Explicit inputs and invocation

First export a bounded panel using `scripts/31_export_temporal_panel.py`. The default EU-Core export layout is `results/phase2/eu_core_temporal_check/panel_edges.csv` and `nodes.csv`. The driver consumes those paths explicitly; it does not create or search for prepared data.

```bash
Rscript r/models/temporal_btergm_ladder.R \
  --input=results/phase2/eu_core_temporal_check/panel_edges.csv \
  --nodes=results/phase2/eu_core_temporal_check/nodes.csv \
  --output-dir=results/models/eu_core_temporal_btergm \
  --bootstrap-reps=20 --degree-decay=0.5 --esp-decay=0.5 \
  --models=all --parallel=no --ncpus=1 --seed=20261013
```

The panel CSV requires `time,from,to`; the node CSV requires `id`. The node file is mandatory and contains the full frozen universe, including isolates. IDs and original time labels are read as character strings, so `001` is never relabeled `1`. Every panel uses exactly the same node count and `nodes.csv` vertex order, and each network is directed, binary, loop-free, and non-multiplex.

There must be **at least two panels**. The driver sorts integer period indices numerically, or `YYYY-MM` labels chronologically, then requires exact unit steps. It rejects gaps, invalid months, and aliased labels such as `1` and `01` occurring as different periods. Thus an export containing consecutive *observed* labels but a missing integer window or calendar month is not treated as consecutive data. Arbitrary lexical labels are rejected rather than assigned a guessed cadence. The edge-list contract cannot represent a completely empty panel; the driver never fills an omitted period or infers coverage outside the supplied range.

Duplicate `(time,from,to)` rows, self-loops, empty labels, duplicate node IDs, and endpoints outside the node universe are rejected. Absent dyads are zeros only within the explicitly supplied universe and listed times. Extra CSV columns are ignored; weights and raw timestamps are not interpreted.

The bounds default to `--max-nodes=100`, `--max-transitions=2`, and `--max-dyads=50000`. The last bound counts `n*(n-1)*(panels-1)` response dyad-time rows. A larger input fails visibly; it is never silently subset. To use a different explicitly bounded panel, change the bounds deliberately and inspect the manifest.

`--models=all` selects every ladder row. A unique comma-separated subset is also supported, for example `--models=T_tt,T0`. Unknown or duplicate labels/options are errors. `--parallel` accepts `no`, `snow`, or `multicore`; `no` and `--ncpus=1` are the portable defaults. `multicore` is rejected on Windows; `snow` uses btergm's documented portable backend. The seed is reset before each model so a model's bootstrap draws do not depend on which other models were selected. Parallel reproducibility is conditional on the backend and installed package versions. `--overwrite=TRUE` permits replacement of this driver's named artifacts only; unrelated files in the output directory are retained.

## Exact specifications

All degree and shared-partner decays are fixed (`fixed=TRUE`) and recorded. The default is 0.5 for each family.

```r
T_tt = edges + edgecov(lag_total_CN)

T0 = edges + mutual +
     memory(type='autoregression', lag=1) + delrecip(lag=1) +
     edgecov(lag_oi) + edgecov(lag_oo) + edgecov(lag_ii) +
     edgecov(lag_outdegree_source) + edgecov(lag_indegree_target)

T1 = T0 + gwodegree(0.5, fixed=TRUE) + gwidegree(0.5, fixed=TRUE)

T2 = T1 + gwesp(0.5, fixed=TRUE, type='OTP') +
          gwesp(0.5, fixed=TRUE, type='OSP') +
          gwesp(0.5, fixed=TRUE, type='ISP')

T2_minus_H = edges + mutual +
             gwodegree(0.5, fixed=TRUE) + gwidegree(0.5, fixed=TRUE) +
             gwesp(0.5, fixed=TRUE, type='OTP') +
             gwesp(0.5, fixed=TRUE, type='OSP') +
             gwesp(0.5, fixed=TRUE, type='ISP')
```

`T2_minus_H` has **no lagged terms**, including no memory or delayed reciprocity. The driver passes the original requested formula to btergm; unsupported terms and numerical failures are recorded without substituting another statistic or estimation engine.

For the lagged adjacency matrix `A = A[t-1]`, rows are sources and columns are targets. The explicit dyadic matrices follow the repository's directed common-neighbor convention:

```r
lag_oi               = A %*% A       # sum_k A[i,k] A[k,j]
lag_oo               = A %*% t(A)    # sum_k A[i,k] A[j,k]
lag_ii               = t(A) %*% A    # sum_k A[k,i] A[k,j]
lag_total_CN         = lag_oi + lag_oo + lag_ii
lag_outdegree_source = rowSums(A)[i] # repeated across targets j
lag_indegree_target  = colSums(A)[j] # repeated across sources i
```

Diagonals are set to zero because self-dyads are excluded. Each matrix has exact node labels in the same order as the directed networks. No matrix for response time `t` uses `A[t]` or a future panel.

### Why the list alignment matters

btergm accepts time-varying `edgecov` lists having the same initial length as the network list. Its `memory` and `delrecip` preprocessing creates lagged lists of length `T-1`, then drops the oldest element from longer network/covariate lists. [1] [2] [3]

For T0/T1/T2, the driver therefore provides **all T networks** and T-length explicit lag lists. Each list has an unused zero placeholder at time 1, followed by matrices computed from the preceding panel. btergm's temporal preprocessing removes that placeholder together with the first dependent panel. Pre-trimming these models would incorrectly lose an additional response panel.

T_tt and T2_minus_H do not contain built-in temporal terms, so their network lists are explicitly trimmed to times 2 through T. T_tt's lag list is trimmed identically. Consequently **all models estimate the same response periods**, even though T2_minus_H omits history. `lag_alignment.csv` records the response/history pairs; the first panel is history only and its placeholder is never estimated.

## Artifacts and visible failures

`model_specs.csv` records the exact formulas, temporal-term flags, estimator, and interpretation. `model_status.csv` reports each selected model's fit/extraction status, errors, warnings, elapsed time, response count, and requested bootstrap replications. A failed model does not stop subsequent selected models.

`coefficients.csv` contains named MPLE coefficients, bootstrap sample standard deviations and finite replication counts where extractable, and 95% percentile bootstrap intervals from `stats::confint(fit, level=0.95, type="perc", invlogit=FALSE)`. [4] Interval errors or unexpected return shapes leave missing bounds and an explicit `ci_status=not_extractable`/message. No Wald interval or probability-scale transformation is substituted. Warnings about dropped or extreme bootstrap replicates are preserved. **The default 20 replicates and few response periods are a bounded pilot, not confirmatory uncertainty estimates.**

`input_summary.csv` records counts, cadence, range, and validated bounds. `panel_summary.csv` records every panel's same-size node/edge counts, while `lag_alignment.csv` records exactly which previous period supplies each response period's lag quantities. `diagnostics.txt` captures summaries and warnings; no MCMC convergence claim is made. `model_objects.rds` retains the fitted btergm objects for inspection, not forecasting.

`run_manifest.json` records input paths and MD5 fingerprints, original node/time ordering, selected models, fixed decays, bounds, package versions, estimator settings, lag definitions, statuses, and explicit `forecasts=false`/`simulated_probabilities=false` guardrails. Missing `btergm`, `network`, or `jsonlite` produces a **base-R failure manifest and nonzero exit**, plus missing-package status rows and empty coefficients; the failure writer does not itself require jsonlite. Invalid inputs/runtime errors also produce failure manifests once an output directory can safely be created. All failed/nonfinite model fits produce a nonzero exit; partial success retains a completed-with-model-failures manifest. An invalid or protected output path cannot receive a failure manifest without violating the no-overwrite policy.

## Dependency-light validation

```bash
Rscript r/tests/test_temporal_btergm_ladder.R
python -m pytest tests/test_temporal_btergm_driver.py
```

The R test sources pure helpers and uses only base/recommended R facilities. It checks exact formulas and defaults, model selection, leading-zero labels, isolate preservation in matrices, consecutive numeric/month panels, strict malformed-input rejection, lag matrix orientation, future-panel independence, list alignment, and the no-prediction API contract. It does **not** install modeling packages or claim that a package fit succeeded. The Python source-contract test runs without R or modeling packages; it also executes the base-R test when `Rscript` is available.

## References

[1]: https://rdrr.io/cran/btergm/man/btergm.html "btergm: Estimate a TERGM by MPLE with temporal bootstrapping"
[2]: https://www.rdocumentation.org/packages/btergm/versions/1.9.13/topics/tergm-terms "btergm temporal dependency terms: memory and delrecip"
[3]: https://github.com/leifeld-lab/btergm/blob/master/R/tergmprepare.R "btergm source: temporal covariate construction and oldest-list-element trimming"
[4]: https://github.com/leifeld-lab/btergm/blob/master/R/btergm.R "btergm source: S4 coefficients, bootstrap samples, and percentile confint method"
