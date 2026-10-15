# Bounded btergm temporal-ladder summary

This is the plan's bounded **btergm MPLE with temporal bootstrap** estimator. It is not a forecasting, simulation, MCMC-MLE, or STERGM result.

## Frozen panel and estimator

- Dataset: `eu_core`
- Panel labels: `0, 1, 2`
- Nodes: 100; response transitions: 2; dyad-time rows: 19800
- Estimator status: `completed`
- Interpretation: T1, T2, and T2_minus_H are MPLE conditional score estimators only; no simulated probability or forecast was computed.

## Model status

- Counts: fit_succeeded=5
- `T_tt`: `fit_succeeded`
- `T0`: `fit_succeeded`
- `T1`: `fit_succeeded`
- `T2`: `fit_succeeded`
- `T2_minus_H`: `fit_succeeded`

## MPLE coefficients and bootstrap-interval availability

| Model | Term | Estimate | 95% bootstrap interval | Interval status |
|---|---|---:|---:|---|
| T_tt | edges | -3.4620 | [-3.5580, -3.3727] | empirical_percentile |
| T_tt | edgecov.lag_total_CN[[i]] | 0.2420 | [0.2352, 0.2493] | empirical_percentile |
| T0 | edges | -4.5410 | [-4.7705, -4.4271] | empirical_percentile |
| T0 | mutual | 3.8901 | [3.7001, 4.0535] | empirical_percentile |
| T0 | edgecov.memory[[i]] | 2.3726 | [2.2380, 2.5721] | empirical_percentile |
| T0 | edgecov.delrecip[[i]] | -0.1460 | [-0.3429, 0.0275] | empirical_percentile |
| T0 | edgecov.lag_oi[[i]] | 0.0984 | [0.0984, 0.1095] | empirical_percentile |
| T0 | edgecov.lag_oo[[i]] | -0.0005 | [-0.0168, -0.0005] | empirical_percentile |
| T0 | edgecov.lag_ii[[i]] | 0.1739 | [0.1350, 0.2145] | empirical_percentile |
| T0 | edgecov.lag_outdegree_source[[i]] | 0.0129 | [0.0043, 0.0238] | empirical_percentile |
| T0 | edgecov.lag_indegree_target[[i]] | 0.0015 | [-0.0148, 0.0262] | empirical_percentile |
| T1 | edges | -4.0870 | [-4.3239, -3.9969] | empirical_percentile |
| T1 | mutual | 3.8884 | [3.7154, 4.0513] | empirical_percentile |
| T1 | edgecov.memory[[i]] | 2.4347 | [2.2800, 2.6599] | empirical_percentile |
| T1 | edgecov.delrecip[[i]] | -0.1044 | [-0.3120, 0.0638] | empirical_percentile |
| T1 | edgecov.lag_oi[[i]] | 0.1128 | [0.1128, 0.1349] | empirical_percentile |
| T1 | edgecov.lag_oo[[i]] | -0.0005 | [-0.0157, -0.0005] | empirical_percentile |
| T1 | edgecov.lag_ii[[i]] | 0.1443 | [0.0966, 0.1818] | empirical_percentile |
| T1 | edgecov.lag_outdegree_source[[i]] | -0.0082 | [-0.0186, 0.0050] | empirical_percentile |
| T1 | edgecov.lag_indegree_target[[i]] | -0.0082 | [-0.0252, 0.0195] | empirical_percentile |
| T1 | gwodeg.fixed.0.5 | -2.7400 | [-3.1313, -2.4226] | empirical_percentile |
| T1 | gwideg.fixed.0.5 | -0.7898 | [-1.1424, -0.3126] | empirical_percentile |
| T2 | edges | -4.6413 | [-4.9182, -4.5731] | empirical_percentile |
| T2 | mutual | 3.6029 | [3.5017, 3.7221] | empirical_percentile |
| T2 | edgecov.memory[[i]] | 2.3393 | [2.1684, 2.5868] | empirical_percentile |
| T2 | edgecov.delrecip[[i]] | -0.0983 | [-0.2664, 0.0349] | empirical_percentile |
| T2 | edgecov.lag_oi[[i]] | 0.1178 | [0.1178, 0.1451] | empirical_percentile |
| T2 | edgecov.lag_oo[[i]] | -0.0455 | [-0.1071, -0.0129] | empirical_percentile |
| T2 | edgecov.lag_ii[[i]] | 0.0506 | [0.0163, 0.0725] | empirical_percentile |
| T2 | edgecov.lag_outdegree_source[[i]] | -0.0180 | [-0.0298, -0.0041] | empirical_percentile |
| T2 | edgecov.lag_indegree_target[[i]] | -0.0052 | [-0.0258, 0.0306] | empirical_percentile |
| T2 | gwodeg.fixed.0.5 | -1.7210 | [-2.1811, -1.3508] | empirical_percentile |
| T2 | gwideg.fixed.0.5 | -0.1304 | [-0.4770, 0.3401] | empirical_percentile |
| T2 | gwesp.OTP.fixed.0.5 | 0.1819 | [-0.0756, 0.4742] | empirical_percentile |
| T2 | gwesp.OSP.fixed.0.5 | -0.0681 | [-0.2953, 0.1240] | empirical_percentile |
| T2 | gwesp.ISP.fixed.0.5 | 0.4311 | [0.3437, 0.5364] | empirical_percentile |
| T2_minus_H | edges | -4.5454 | [-4.5813, -4.5454] | empirical_percentile |
| T2_minus_H | mutual | 4.1643 | [4.1369, 4.2085] | empirical_percentile |
| T2_minus_H | gwodeg.fixed.0.5 | -1.3204 | [-1.6397, -1.0384] | empirical_percentile |
| T2_minus_H | gwideg.fixed.0.5 | 0.0182 | [-0.1480, 0.1356] | empirical_percentile |
| T2_minus_H | gwesp.OTP.fixed.0.5 | 0.2674 | [0.0050, 0.6075] | empirical_percentile |
| T2_minus_H | gwesp.OSP.fixed.0.5 | -0.0181 | [-0.2238, 0.1495] | empirical_percentile |
| T2_minus_H | gwesp.ISP.fixed.0.5 | 0.4473 | [0.3370, 0.5383] | empirical_percentile |

Inspect `model_status.csv`, `diagnostics.txt`, and `coefficients.csv` before interpreting any term. With only 20 bootstrap replicates and two response transitions, intervals are pilot diagnostics—not confirmatory uncertainty estimates.
