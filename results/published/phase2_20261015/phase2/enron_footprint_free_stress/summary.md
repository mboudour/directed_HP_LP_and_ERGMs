# Footprint-free directed formal-concept stress test

- Dataset: `enron`
- Full capped concepts: `232`
- Requested selected target fraction: `0.300`
- Selected target footprints are pairwise arc-disjoint; every target arc is removed from the observed graph.
- Any original concept sharing a removed target arc is absent from the training concept section.
- Scores are uncalibrated lifted directed-LP rankings; this is a strict Regime C stress test.

| Replicate | Selected | Local targets | Removed arcs | Removed arc rate | Random panel positives | Degree panel positives |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 52 | 19 | 254 | 0.4000 | 18 | 18 |
| 2 | 53 | 17 | 273 | 0.4299 | 16 | 16 |
| 3 | 55 | 15 | 269 | 0.4236 | 15 | 14 |

Metric summaries are in `metric_summary.csv`; unavailable panel cells are not replaced with easier negatives.
