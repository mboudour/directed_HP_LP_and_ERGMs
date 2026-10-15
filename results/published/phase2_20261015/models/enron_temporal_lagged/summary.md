# Bounded chronological check summary

This result is a factorized lagged conditional check. It is not a full TERGM, STERGM, relational hyperevent model, or forecasting result.

## Frozen chronological panel

- Dataset: `enron`
- Selected panel labels: `1999-05, 1999-06, 1999-07`
- Nodes: 100; transitions: 2; factorized dyad-time rows: 19800
- Outcome ties: 10; outcome rate: 0.000505

## Factorized model status

- `L0`: `fit_succeeded`
- `L1_persistence`: `fit_succeeded`
- `L2_persistence_lagged_oo`: `fit_succeeded`

## Lagged coefficients

| Model | Term | Estimate | Odds ratio |
|---|---|---:|---:|
| L0 | (Intercept) | -7.590347 | 0.000505 |
| L1_persistence | (Intercept) | -8.506436 | 0.000202 |
| L1_persistence | lag_tie | 8.911901 | 7419.750000 |
| L2_persistence_lagged_oo | (Intercept) | -8.506284 | 0.000202 |
| L2_persistence_lagged_oo | lag_tie | 9.199431 | 9891.500000 |
| L2_persistence_lagged_oo | lag_cn_out | -16.342704 | 0.000000 |

## Proposition 6 numerical identity

- Status: `passed`
- Interpretation: with a positive coefficient on lagged shared outgoing neighbours, the fitted logistic score and that count have the same strict ranking.

## Package guardrails

- `btergm` requested as `check`: `available_not_fit`
- `tergm` requested as `check`: `available_placeholder_not_fit`

The package statuses above are availability/guardrail checks only. No full temporal ERGM or STERGM has been fitted or claimed by this bounded analysis.
