# Footprint-free directed formal-concept stress test

- Dataset: `mathoverflow`
- Full capped concepts: `207`
- Requested selected target fraction: `0.300`
- Selected target footprints are pairwise arc-disjoint; every target arc is removed from the observed graph.
- Any original concept sharing a removed target arc is absent from the training concept section.
- Scores are uncalibrated lifted directed-LP rankings; this is a strict Regime C stress test.

| Replicate | Selected | Local targets | Removed arcs | Removed arc rate | Random panel positives | Degree panel positives |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37 | 12 | 258 | 0.2529 | 12 | 12 |
| 2 | 36 | 19 | 243 | 0.2382 | 19 | 19 |
| 3 | 43 | 14 | 295 | 0.2892 | 14 | 14 |

Metric summaries are in `metric_summary.csv`; unavailable panel cells are not replaced with easier negatives.
