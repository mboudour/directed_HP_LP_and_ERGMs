# Footprint-free directed formal-concept stress test

- Dataset: `caviar`
- Full capped concepts: `80`
- Requested selected target fraction: `0.300`
- Selected target footprints are pairwise arc-disjoint; every target arc is removed from the observed graph.
- Any original concept sharing a removed target arc is absent from the training concept section.
- Scores are uncalibrated lifted directed-LP rankings; this is a strict Regime C stress test.

| Replicate | Selected | Local targets | Removed arcs | Removed arc rate | Random panel positives | Degree panel positives |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 24 | 9 | 101 | 0.3424 | 9 | 9 |
| 2 | 24 | 5 | 105 | 0.3559 | 5 | 5 |
| 3 | 24 | 7 | 103 | 0.3492 | 7 | 7 |

Metric summaries are in `metric_summary.csv`; unavailable panel cells are not replaced with easier negatives.
