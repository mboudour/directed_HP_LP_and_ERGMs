# Conditional ERGM joint-footprint simulation

This workflow implements the plan’s **static conditional graph-footprint score**
\(L3\)-F:

\[
L3\text{-F}(T,H) = P_{\hat\theta}(T\times H \subseteq A \mid O).
\]

It is deliberately distinct from the existing `L1`, `L1g`, and conditional-
pseudolikelihood product pilot. It never estimates the probability that a recorded
Enron email event occurred.

## Observation convention

For a candidate footprint, the observed split projection is the observation set
\(O\):

- every split-specific observed dyad, whether an arc or a non-arc, is fixed;
- an arc already observed because another recorded event type induced it is fixed
  at one—it is genuine evidence, not leakage;
- only footprint dyads absent from that projection are declared missing for the
  candidate-specific simulation.

The R driver materializes the last item with the `network` package’s missing-edge
representation and calls Statnet simulation with `constraints = ~observed`. This
lets the Markov chain change only the candidate’s unknown footprint dyads.

In the same draws, the driver estimates each unknown dyad’s marginal probability
and reports:

| Quantity | Estimate |
|---|---|
| `L1` | Mean footprint support, assigning observed footprint arcs probability 1. |
| `L1g` | Geometric mean support on the same scale. |
| `L2` | Product of the candidate-specific marginal probabilities. |
| `L3_F` | Fraction of conditional completions with the entire footprint present. |
| `delta_dep` | `log(L3_F) - log(L2)` when both Monte Carlo estimates are positive. |

Thus `L2` and `L3_F` share precisely the same observation constraints. Their
contrast is interpretable as within-footprint dependence rather than a difference
in what information is conditioned on.

## Bounded pilot design

The initial Enron run is a deliberately small **smoke test**, not a final
performance comparison:

- it fits `M1` only, on frozen split `mcar_replicate_001`;
- `M1` is the dyad-factorizing validation model;
- it selects at most one candidate per panel/label (six candidates at most);
- only candidates with at most two footprint dyads unobserved in the split are
  eligible; this avoids presenting a zero count from naive Monte Carlo as an
  estimate of an extremely rare large-footprint probability;
- each eligible candidate receives 100 conditional completions; and
- MCMLE uses five iterations at most, 256 simulated networks per iteration, and
  deliberately sets `eval.loglik = FALSE`. The latter removes bridge sampling,
  which calculates an unnecessary normalizing constant for this score-only
  diagnostic.

This smoke test first establishes that the observation constraint, MCMLE fit,
and conditional simulation work end-to-end on the local machine. It does not
test higher-order dependence: `M4` and multi-split / larger-draw calculations
remain separate, explicitly scaled computations only after this check has been
reviewed.

A candidate with a wholly observed footprint has `L3_F = L2 = 1` by conditioning,
without simulation. If a simulated `L3_F` is zero, it is **not** reported as an
exact zero probability or supplied with a finite log-dependence score. Instead,
`L3_F_zero_upper95 = 3/nsim` is given as a standard rule-of-three upper bound.

No ROC-AUC, PR-AUC, coefficient inference, native-event probability, or automatic
MCMLE adequacy claim is emitted by this pilot. `diagnostics/` stores the full
MCMC-diagnostic text for manual review. Simulation feasibility is not a substitute
for the planned GOF checks (degree, reciprocity, triad census, and shared partners)
before any model-based result is interpreted substantively.

## Run

After the frozen event-first inputs are available:

```zsh
make phase2-enron-joint-footprints
```

The target regenerates the deterministic frozen input export and replaces only the
ignored local smoke-test output bundle:

```text
results/models/enron_joint_footprint_mcmle_smoke/
```

The most important files are:

- `summary.md` — completion and interpretation boundary;
- `model_status.csv` — separate MCMLE outcomes for every split and model;
- `candidate_simulation_scores.csv` — candidate-specific `L1`, `L1g`, `L2`,
  `L3_F`, Monte Carlo SE, zero-score bound, and dependence increment;
- `selected_candidates.csv` — the actual bounded candidate subset; and
- `diagnostics/` plus `fitted_models/` — MCMLE diagnostic output and reproducible
  fitted model objects.

## Relation to the prior factorized pilot

`r/models/score_native_event_footprints.R` uses
`predict(..., conditional = TRUE)` on split-specific MPLE fits. Its output is a
valuable conditional-pseudolikelihood **ranking pilot**, but its `L2` column is a
product of single-dyad conditional scores. It does not by itself put all arcs of a
candidate footprint under one shared observation constraint and therefore is not
the `L2` used for the formal \(L3\)-F dependence increment. The present workflow
supplies the matched conditional-simulation version.

Source evidence and Statnet API notes are retained in
[`research_conditional_ergm_simulation_sources.md`](research_conditional_ergm_simulation_sources.md).
