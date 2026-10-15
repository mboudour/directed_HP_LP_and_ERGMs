# Degree-preserving fidelity rewiring null

## Purpose

This module supplies the chance baseline required for the native-event versus
formal-concept representation-fidelity analysis. It asks whether the observed
agreement remains high after preserving each actor's directed activity profile.

## Null model

For Enron's fixed core-100 node universe, the strict recorded native-event types
remain fixed. The aggregate static digraph is rewired by simple directed
double-edge swaps:

\[
(i,j),(k,l) \mapsto (i,l),(k,j).
\]

Each accepted swap preserves every node's out-degree and in-degree, prohibits
loops and duplicate arcs, and does not alter the number of arcs. The primary
run uses 100 independently seeded rewires and 10 successful swaps per observed
arc (6,350 swaps per rewire).

## Comparison

For the observed graph and every rewired graph, we enumerate the cap-first
formal-concept section with `|T|, |H| <= 3`. We compare it with the same
cap-eligible native event types using:

- exact ordered tail/head matches;
- formal-concept precision and native-event recall under exact equality;
- footprint Jaccard and directional footprint coverage;
- best role-sensitive Jaccard similarity in both directions; and
- the number of capped concepts without an exact event-type match.

The output reports the null mean, null standard deviation, z-score, and a
one-sided empirical probability `P(null >= observed)`, with the standard
`(1 + count) / (1 + rewires)` correction. The p-values are descriptive and are
not corrected for multiple comparisons.

## Interpretation boundary

This is a static representation-fidelity null, not a missingness, temporal, or
ERGM null. It evaluates whether the observed aggregate graph aligns with the
recorded event types beyond its in- and out-degree sequences. It does **not**
make formal concepts into reconstructed native events.

## Reproduction

```bash
make phase2-enron-fidelity-rewire
```

The command writes the private local bundle to
`results/phase2/enron_fidelity_rewire_null/`. The aggregate `summary.md`,
comparison table, and non-sensitive per-rewire metrics are copied into the
versioned private publication bundle by `make phase2-publish-aggregate`.
