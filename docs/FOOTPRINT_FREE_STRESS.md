# Regime C: footprint-free formal-concept stress test

## Purpose

Regime C is the conservative stress test in the agreed plan. Unlike Regime B,
where a held-out formal concept may retain some of its footprint through other
observed structure, the selected Regime C targets have **no target footprint
arcs left in the observed digraph**.

## Target selection and masking

For every static dataset, the procedure:

1. enumerates the cap-first (`|T|, |H| <= 3`) formal-concept section of the
   full relation;
2. restricts the candidate target set to non-singleton footprints;
3. uses a seeded greedy procedure to select up to 30% of eligible concepts with
   pairwise arc-disjoint footprints;
4. removes the union of selected footprints from the graph; and
5. re-enumerates the observed concept section.

Since every selected footprint is removed, every full-graph concept sharing at
least one selected arc is absent from the training concept section. The output
explicitly records the selection count, removal rate, observed arcs, and the
number of original concepts lost from training. If a selected concept no longer
satisfies the observed-graph weak-distance-two candidate rule, it is excluded
from scoring and counted as unavailable rather than replaced.

## Evaluation

Selected, locally eligible concepts are positives. Random and observed
role-degree-decile-matched true non-concepts with identical tail/head arities
are balanced negative panels. All candidates are evaluated with the same
uncalibrated lifted directed LP scores used in Regime B. The output provides
ROC-AUC, PR-AUC, precision@k, and recall@k per panel, score, and replicate.

This is a **ranking stress test**, not calibration, native-event recovery, or a
joint ERGM probability estimate. Sparse panels are reported as unavailable;
they are not substituted with easy random negatives.

## Reproduction

```bash
make phase2-enron-footprint-free
make phase2-eu-core-footprint-free
make phase2-caviar-footprint-free
make phase2-mathoverflow-footprint-free
```

Aggregate-only summaries enter the private versioned publication bundle through
`make phase2-publish-aggregate`.
