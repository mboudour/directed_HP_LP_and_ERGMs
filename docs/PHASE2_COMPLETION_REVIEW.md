# Phase 2 completion review

**Review date:** 2026-10-15
**Plan followed:** *ERGM Benchmark for Directed Link and Hyperlink Prediction*
**Purpose:** close the plan’s Phase 2 pilot gates, label admissible evidence,
and prevent pilot/sensitivity calculations from being presented as primary
results.

## Pilot-gate status

| Plan gate | Status | Evidence and consequence |
|---|---|---|
| 1. Data provenance and target eligibility | **Passed with scope restrictions** | Enron and MathOverflow provide native directed event targets; EU-core provides directed temporal arcs; CAVIAR is static dyadic/footprint-only. Ciel remains blocked by unresolved orientation. Jmail remains audit-only pending admissibility. |
| 2. Representation | **Passed as a diagnostic, not a claim of event recovery** | Capped concept audits were completed on each analysis core. Enron’s formal concepts cover many dyadic footprints but have zero exact native-event-type matches; this confirms that concepts and events must remain distinct targets. Regime-C footprint-free stress tests have been run separately. |
| 3. ERGM | **Partly passed** | Static MPLE ladder fits and conditional-score branches run on Enron and CAVIAR (plus available static cores). The Enron MCMC-MLE feasibility gate failed to mix/converge even after the deterministic core-50 reduction. Therefore MCMC-based L3 simulation is **not** a primary Enron result; the bounded M4 MPLE joint calculation is a labelled sensitivity only. |
| 4. NHP-D neural benchmark | **Not passed** | The official source archive lacks a bundled directed dataset and fails its compatibility probes. No neural result is admitted; see `docs/NHPD_REPRODUCTION_GATE.md`. |
| 5. Scope | **Resolved for Paper 1** | Keep Regimes A/B as the main missingness study. Treat Regime C and the rate/MNAR-in analyses as supplements. Exclude Regime K and combined masking-and-forecasting from Paper 1. |
| 6. Chronological check | **Bounded only** | Factorized history baseline and btergm MPLE ladder outputs exist for Enron/EU-core. They remain a chronological diagnostic: no forecasting claim or same-specification MCMC-MLE simulation is admitted. |

## Primary evidence set for Paper 1

1. **Static directed-arc missingness:** directed LP and ERGM conditional-score
   analyses on the eligible static cores. The static ERGM ladder's MPLE results
   must be described as conditional scoring rather than joint probabilities.
2. **Formal-concept target (Regime B):** cap-first enumeration, arc-first
   concept recovery, and the degree-preserving fidelity null, reported as a
   structural target distinct from recorded events.
3. **Native-event target (Regime A):** Enron and MathOverflow only, using
   event-first type masks, random and directed hard panels, and fixed-role
   assignment.
4. **Masked ERGM footprint scores:** factorized conditional-pseudolikelihood
   footprint scores `L1`, `L1g`, and `L2` in their labelled scope. The
   30-mask paired analysis delivers uncertainty for the primary native-event
   branches without pooling masks across datasets.
5. **Bounded chronological check:** Enron/EU-core history versus
   contemporaneous-score diagnostics, described as a check of the plan’s
   score-decomposition logic—not a forecasting study.

## Supplementary or excluded evidence

| Item | Treatment | Reason |
|---|---|---|
| Regime C footprint-free concept stress | Supplement | Deliberate stress test, not main missingness regime. |
| MNAR-in and mask-rate grid | Supplement | Section 9.1 labels them focused/supplementary. |
| Degree-preserving fidelity rewiring null | Supplement | Falsification diagnostic, not a predictor benchmark. |
| M4 MPLE joint-footprint sensitivity | Supplement / feasibility record | It is not an MCMC-MLE-derived joint probability and cannot establish L3-F. |
| L3-F/L3-C MCMC simulation on Enron | Excluded from primary claim | MCMC-MLE feasibility gate failed. |
| NHP-D | Excluded | Reproduction gate failed; no defensible directed result. |
| Regime K and masking-plus-forecasting | Excluded from Paper 1 | Explicitly deferred by the agreed scope decision. |
| STERGM/RHEM and native-event forecasting | Deferred to Paper 2 | They require a separate forecasting framing, competition set, and formation/persistence design. |

## Quality and provenance controls completed

- Exact uploaded data snapshot used for autonomous computation is documented in
  `docs/DATA_SNAPSHOT_IMPORT.md`.
- Public repository is private.
- Source code, small audit metadata, aggregate output tables, checksums, and
  execution records are tracked; raw emails, raw archives, address-bearing maps,
  full candidate panels, and per-event predictions remain excluded.
- Project validation after the final gate: Python formatting/lint checks,
  **64 passed / 1 skipped** Python tests, and all four R model-driver contract
  tests passed.

## Conclusion

Phase 2 is **complete as a pilot-and-computation phase**. It did not make every
planned method admissible; that is an informative result of the plan’s gates,
not an unfinished computation. The next work phase is manuscript construction:
write only to the admissible-evidence boundary above, make exclusions explicit,
and keep Paper 2’s forecasting study separate.
