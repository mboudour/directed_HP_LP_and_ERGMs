# Arc-first formal-concept recovery

`scripts/46_run_arcfirst_concept_recovery.py` evaluates **formal-concept recovery** without relabelling concepts as recorded group events.

## Target and observation rule

For a static directed relation `D = (V, A)`, the driver first enumerates the declared cap-first formal-concept section of the full graph. In each split, it masks arcs by the requested mechanism and derives a separate observed graph `D_obs`.

A positive is a full-graph formal concept `(T, H)` that is **lost** from the formal-concept section of `D_obs`. This implements the plan's arc-first Regime B target: concepts of the original graph that are no longer available after missing ties are introduced. A positive may have some or even all of its footprint arcs still observed, because maximality can be lost independently of footprint completeness; this is reported by `already_observed_footprint` rather than treated as leakage.

The candidate universe is constructed from the observed split only. Every participant pair must be within weak distance two in `D_obs`. The script rejects all full-graph formal concepts from negative panels, so a negative cannot be an observed training concept or an unobserved true concept.

## Negative panels

Each split writes the following separately labelled, arity-matched panels:

| Panel | Negative construction | Purpose |
|---|---|---|
| `random` | Random true non-concepts matched exactly on `(|T|, |H|)` | Continuity baseline |
| `degree_matched` | True non-concepts matched on tail out-degree and head in-degree rank deciles in `D_obs` | Activity/popularity control |
| `nonmaximal_complete` | Complete observed footprints that are non-maximal true non-concepts | Maximality stress test |

The non-maximal panel can be sparse. The driver reports its available subset and **does not** replace it with easier random negatives. All completed panels are balanced, but their positive count may be below the number of eligible lost concepts where an exact matching negative cannot be constructed.

## Scores and boundaries

The current implementation scores uncalibrated lifted directed LP features: OI, OO, II, their total, and their directed Adamic--Adar variants. It reports ROC-AUC, PR-AUC, precision@k, and recall@k only.

This is **not** the ERGM joint concept probability `L3-C`. `L3-C`, its Monte Carlo error, the maximality increment, and the full score-gap/Shapley decomposition require the separately gated conditional ERGM simulation branch.

## Reproducible targets

The four admitted static datasets use the frozen main-rate contract: cap `(3,3)`, 30% arc-first masking, three replicates per mechanism, and MCAR plus MNAR-out. They are invoked through:

```zsh
make phase2-enron-concept-recovery
make phase2-eu-core-concept-recovery
make phase2-caviar-concept-recovery
make phase2-mathoverflow-concept-recovery
```

Each target replaces only its named `results/phase2/*_concept_recovery/` bundle. All row-level predictions remain local and ignored by Git; the aggregate collector can publish only the non-sensitive summary tables.
