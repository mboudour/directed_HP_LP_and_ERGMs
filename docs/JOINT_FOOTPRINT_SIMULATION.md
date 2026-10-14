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
| `delta_dep_mcse`, interval | Nonparametric bootstrap uncertainty for `delta_dep`, resampling the independent conditional completions. |

Thus `L2` and `L3_F` share precisely the same observation constraints. Their
contrast is interpretable as within-footprint dependence rather than a difference
in what information is conditioned on.

## Bounded pilot design

The initial Enron run is a deliberately small **smoke test**, not a final
performance comparison:

- it fits `M1` only, on frozen split `mcar_replicate_001`;
- `M1` is the dyad-factorizing validation model;
- it selects at most one candidate per panel/label (six candidates at most);
- eligible candidates have **exactly two** unobserved footprint dyads, so the
  calculation is genuinely joint rather than a one-dyad tautology;
- each unknown dyad's reverse must already be observed. For `M1`, this yields a
  deliberately well-supported, nontrivial factorization check: each unknown
  arc has reciprocal evidence while the candidate does not include both arcs of
  any reciprocal pair;
- each eligible candidate receives 200 conditional completions; and
- each completion begins from the same candidate-specific observed basis rather
  than continuing one Markov chain. This deliberately slower choice makes the
  reported binomial Monte Carlo SE for `L3-F` appropriate for this small smoke
  test; and
- MCMLE uses five iterations at most, 256 simulated networks per iteration, and
  deliberately sets `eval.loglik = FALSE`. The latter removes bridge sampling,
  which calculates an unnecessary normalizing constant for this score-only
  diagnostic.

This smoke test first establishes that the observation constraint, M1 MCMLE fit,
and conditional simulation work end-to-end on a **multi-dyad** footprint. Its
M1 result should have `L3-F` close to the same-draw `L2`, within Monte Carlo
error. It does not test higher-order dependence: `M4` and multi-split /
larger-draw calculations remain separate, explicitly scaled computations only
after this check has been reviewed.

The M4 MCMLE feasibility gate failed on the 100-node Enron split: after four
non-converged iterations, Statnet adaptively increased the fifth MCMC sample and
the interactive run was stopped after more than nine minutes. This is recorded
as an MCMLE mixing/convergence gate failure, not as a result and not as a
computer-performance problem.

The next deliberately bounded stage is therefore a separate `M4` **MPLE
parameter-plug-in sensitivity** on the same single split and candidate-selection
rule. It tests whether a closure-capable fitted parameter vector can be
conditionally simulated and reports a bootstrap interval for its
within-footprint increment. It is explicitly not an MCMLE estimate, not a
substantive M4 result, and not a comparison across targets, models, or
missingness mechanisms.

A candidate with a wholly observed footprint has `L3_F = L2 = 1` by conditioning,
without simulation. If a simulated `L3_F` is zero, it is **not** reported as an
exact zero probability or supplied with a finite log-dependence score. Instead,
`L3_F_zero_upper95 = 3/nsim` is given as a standard rule-of-three upper bound.

No ROC-AUC, PR-AUC, coefficient inference, native-event probability, or automatic
fit-adequacy claim is emitted by this pilot. `diagnostics/` stores the available
fit diagnostic text for manual review. Simulation feasibility is not a substitute
for the planned GOF checks (degree, reciprocity, triad census, and shared partners)
before any model-based result is interpreted substantively.

## Run

After the frozen event-first inputs are available:

```zsh
make phase2-enron-joint-footprints
```

Only after the M1 factorization check has completed should the bounded M4 MPLE
sensitivity be invoked:

```zsh
make phase2-enron-joint-m4-mple-sensitivity
```

The target regenerates the deterministic frozen input export and replaces only the
ignored local smoke-test output bundle:

```text
results/models/enron_joint_footprint_mcmle_smoke/
```

The most important files are:

- `summary.md` — completion and interpretation boundary;
- `model_status.csv` — separate fit outcomes for every split and model;
- `candidate_simulation_scores.csv` — candidate-specific `L1`, `L1g`, `L2`,
  `L3_F`, Monte Carlo SE, zero-score bound, dependence increment, and bootstrap
  uncertainty summaries;
- `candidate_simulation_draws.csv` — dyad states from the independent conditional
  completions, retained to audit the bootstrap calculation;
- `selected_candidates.csv` — the actual bounded candidate subset; and
- `diagnostics/` plus `fitted_models/` — available diagnostic output and
  reproducible fitted model objects.

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
