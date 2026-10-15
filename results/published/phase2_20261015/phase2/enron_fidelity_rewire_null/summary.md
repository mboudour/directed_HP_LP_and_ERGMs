# Degree-preserving rewiring null for representation fidelity

- Dataset: `enron_20150507`
- Directed rewires: `100`
- Successful double-edge swaps per rewire: `6,350`
- Native event types are held fixed; only the aggregated directed relation is rewired.

| Metric | Observed | Null mean | Null SD | z | Empirical p (>= observed) |
|---|---:|---:|---:|---:|---:|
| formal_concepts | 232.000000 | 340.330000 | 13.250542 | -8.176 | 1.000000 |
| exact_pairs | 0.000000 | 0.000000 | 0.000000 | nan | 1.000000 |
| concept_precision | 0.000000 | 0.000000 | 0.000000 | nan | 1.000000 |
| event_recall | 0.000000 | 0.000000 | 0.000000 | nan | 1.000000 |
| footprint_jaccard | 0.856693 | 0.058404 | 0.006259 | 127.549 | 0.009901 |
| native_footprint_coverage | 0.866242 | 0.107166 | 0.010891 | 69.699 | 0.009901 |
| concept_footprint_coverage | 0.987296 | 0.113625 | 0.011518 | 75.853 | 0.009901 |
| mean_event_to_concept_role_similarity | 0.421581 | 0.306446 | 0.003307 | 34.817 | 0.009901 |
| mean_concept_to_event_role_similarity | 0.475216 | 0.374103 | 0.008419 | 12.009 | 0.009901 |
| spurious_closure_concepts | 232.000000 | 340.330000 | 13.250542 | -8.176 | 1.000000 |

Positive z values indicate greater observed agreement than the degree-preserving null. The one-sided empirical p column is descriptive and is not a multiple-testing correction.
