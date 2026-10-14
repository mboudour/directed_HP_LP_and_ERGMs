# Bounded EU-core chronological check

The first paper does **not** become a forecasting study. This repository therefore treats
the temporal component as a small, reproducible check of the plan's precise distinction:
lagged network history is factorized, whereas any contemporaneous dependence would require
a joint model and cannot be recovered from history alone.

## Single target

After `make phase2-audits` has prepared EU-core, run:

```zsh
make phase2-eu-core-temporal
```

The target freezes the earliest three available nonempty **30-day** core-100 windows
(labels `0`, `1`, `2`) without looking at outcomes, yielding exactly two adjacent
transitions. It then fits the bounded factorized ladder and writes a concise local report.
The deterministic earliest-window rule is a screening choice for this bounded check; it is
not a claim that those windows constitute a final forecasting test set.

## Models

For each ordered non-self dyad and each transition, the response is
\(T_{tt}=y_{ij,t}\). The right-hand side is progressively expanded:

- `T0`: intercept only;
- `T1`: `T0` plus the lagged tie \(y_{ij,t-1}\);
- `T2`: `T1` plus the lagged shared-outgoing-neighbour count
  \(\sum_k y_{ik,t-1}y_{jk,t-1}\).

All covariates are lagged. Thus these are factorized logistic diagnostic models, not jointly
normalized TERGMs, STERGMs, fitted formation/dissolution processes, or forecasts. The
exported `proposition6_identity.csv` checks the planned ranking identity numerically.

## Outputs

- Panel contract: `results/phase2/eu_core_temporal_check/`.
- Models and automatic report: `results/models/eu_core_temporal_lagged/`.

The report records factorized coefficients, panel size, selected labels, the Proposition 6
identity, and visible `btergm`/`tergm` availability guardrails. It does not fit either
package by default and does not claim their coefficients.
