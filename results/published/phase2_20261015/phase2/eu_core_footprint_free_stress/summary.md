# Footprint-free directed formal-concept stress test

- Dataset: `eu_core`
- Full capped concepts: `45`
- Requested selected target fraction: `0.300`
- Selected target footprints are pairwise arc-disjoint; every target arc is removed from the observed graph.
- Any original concept sharing a removed target arc is absent from the training concept section.
- Scores are uncalibrated lifted directed-LP rankings; this is a strict Regime C stress test.

| Replicate | Selected | Local targets | Removed arcs | Removed arc rate | Random panel positives | Degree panel positives |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | 10 | 103 | 0.0384 | 10 | 10 |
| 2 | 14 | 14 | 108 | 0.0403 | 14 | 14 |
| 3 | 14 | 10 | 114 | 0.0425 | 10 | 10 |

Metric summaries are in `metric_summary.csv`; unavailable panel cells are not replaced with easier negatives.
