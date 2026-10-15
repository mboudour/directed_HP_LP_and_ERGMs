# Bounded btergm temporal-ladder summary

This is the plan's bounded **btergm MPLE with temporal bootstrap** estimator. It is not a forecasting, simulation, MCMC-MLE, or STERGM result.

## Frozen panel and estimator

- Dataset: `enron`
- Panel labels: `1999-05, 1999-06, 1999-07`
- Nodes: 100; response transitions: 2; dyad-time rows: 19800
- Estimator status: `completed_with_model_failures`
- Interpretation: T1, T2, and T2_minus_H are MPLE conditional score estimators only; no simulated probability or forecast was computed.

## Model status

- Counts: fit_nonfinite_coefficients=2, fit_succeeded=3
- `T_tt`: `fit_succeeded`
- `T0`: `fit_succeeded`
- `T1`: `fit_succeeded`
- `T2`: `fit_nonfinite_coefficients` — Nonfinite MPLE coefficients; inspect numerical identification and separation.
- `T2_minus_H`: `fit_nonfinite_coefficients` — Nonfinite MPLE coefficients; inspect numerical identification and separation.

## MPLE coefficients and bootstrap-interval availability

| Model | Term | Estimate | 95% bootstrap interval | Interval status |
|---|---|---:|---:|---|
| T_tt | edges | -7.6950 | [-8.5054, -7.2537] | empirical_percentile |
| T_tt | edgecov.lag_total_CN[[i]] | 5.0559 | [5.0559, 5.8664] | empirical_percentile |
| T0 | edges | -9.3998 | [-40.0939, -9.3998] | empirical_percentile |
| T0 | mutual | 9.1739 | [-1.9859, 27.1002] | empirical_percentile |
| T0 | edgecov.memory[[i]] | 8.0877 | [8.0877, 40.0939] | empirical_percentile |
| T0 | edgecov.delrecip[[i]] | -18.1117 | [-19.4663, 17.4824] | empirical_percentile |
| T0 | edgecov.lag_oi[[i]] | 1.7381 | [1.7381, 19.7027] | empirical_percentile |
| T0 | edgecov.lag_oo[[i]] | -18.5339 | [-22.1498, -18.5339] | empirical_percentile |
| T0 | edgecov.lag_ii[[i]] | -20.7213 | [-22.5072, -20.7213] | empirical_percentile |
| T0 | edgecov.lag_outdegree_source[[i]] | 0.9283 | [-0.0000, 22.1374] | empirical_percentile |
| T0 | edgecov.lag_indegree_target[[i]] | 0.7843 | [-0.0000, 4.0466] | empirical_percentile |
| T1 | edges | -7.4121 | [-192.0078, -7.4121] | empirical_percentile |
| T1 | mutual | 10.9042 | [0.7528, 27.7591] | empirical_percentile |
| T1 | edgecov.memory[[i]] | 9.6040 | [9.6040, 47.0313] | empirical_percentile |
| T1 | edgecov.delrecip[[i]] | -20.4676 | [-20.4676, 1.5937] | empirical_percentile |
| T1 | edgecov.lag_oi[[i]] | 1.3599 | [1.3599, 45.6848] | empirical_percentile |
| T1 | edgecov.lag_oo[[i]] | -22.1122 | [-22.1122, 0.4017] | empirical_percentile |
| T1 | edgecov.lag_ii[[i]] | -21.8546 | [-21.8546, 2.1880] | empirical_percentile |
| T1 | edgecov.lag_outdegree_source[[i]] | -1.9022 | [-1.9022, 20.3337] | empirical_percentile |
| T1 | edgecov.lag_indegree_target[[i]] | 3.8672 | [3.3918, 43.0736] | empirical_percentile |
| T1 | gwodeg.fixed.0.5 | -9.1142 | [-9.1142, 82.5296] | empirical_percentile |
| T1 | gwideg.fixed.0.5 | 4.9990 | [4.9990, 78.2701] | empirical_percentile |
| T2 | edges | -7.3886 | [-192.0078, -7.3886] | empirical_percentile |
| T2 | mutual | 10.8989 | [0.7528, 28.1338] | empirical_percentile |
| T2 | edgecov.memory[[i]] | 9.6014 | [9.6014, 47.0313] | empirical_percentile |
| T2 | edgecov.delrecip[[i]] | -20.4448 | [-21.0314, 1.5937] | empirical_percentile |
| T2 | edgecov.lag_oi[[i]] | 1.3608 | [1.3608, 45.6848] | empirical_percentile |
| T2 | edgecov.lag_oo[[i]] | -22.0616 | [-22.0616, 0.4017] | empirical_percentile |
| T2 | edgecov.lag_ii[[i]] | -21.8540 | [-21.8540, 2.1880] | empirical_percentile |
| T2 | edgecov.lag_outdegree_source[[i]] | -1.8976 | [-1.8976, 20.7125] | empirical_percentile |
| T2 | edgecov.lag_indegree_target[[i]] | 3.8578 | [3.3918, 44.5518] | empirical_percentile |
| T2 | gwodeg.fixed.0.5 | -9.1065 | [-9.1065, 82.5296] | empirical_percentile |
| T2 | gwideg.fixed.0.5 | 4.9732 | [4.9732, 78.2701] | empirical_percentile |
| T2 | gwesp.OTP.fixed.0.5 | -12.1242 | [-13.6337, -12.1242] | empirical_percentile |
| T2_minus_H | edges | -1.0303 | [-56.8044, -0.0173] | empirical_percentile |
| T2_minus_H | mutual | 6.6631 | [-12.1190, 7.5237] | empirical_percentile |
| T2_minus_H | gwodeg.fixed.0.5 | -4.8168 | [-5.7853, 24.3820] | empirical_percentile |
| T2_minus_H | gwideg.fixed.0.5 | -2.9025 | [-3.6937, 24.3820] | empirical_percentile |
| T2_minus_H | gwesp.OTP.fixed.0.5 | -12.6312 | [-14.0981, -12.6312] | empirical_percentile |

Omitted 4 blank or nonfinite coefficient row(s); their model-level diagnostics remain in `model_status.csv`.

Inspect `model_status.csv`, `diagnostics.txt`, and `coefficients.csv` before interpreting any term. With only 20 bootstrap replicates and two response transitions, intervals are pilot diagnostics—not confirmatory uncertainty estimates.
