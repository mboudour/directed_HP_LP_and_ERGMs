# Native-event role-assignment evaluation

- Dataset: `mathoverflow_stackexchange_2024`
- Target: assign the known participants of each held-out event to its fixed tail/head arities.
- Candidate set: every compatible partition; no random case-control prevalence is implied.
- Metrics use uniform tie-breaking expectations and are reported overall through arity rows.

## Split coverage

| Mechanism | Replicate | Held-out types | Evaluated types | Mean partitions |
|---|---:|---:|---:|---:|
| mcar | 1 | 321 | 321 | 2.20 |
| mcar | 2 | 321 | 321 | 2.18 |
| mcar | 3 | 321 | 321 | 2.19 |
| mnar_out | 1 | 330 | 330 | 2.21 |
| mnar_out | 2 | 314 | 314 | 2.25 |
| mnar_out | 3 | 310 | 310 | 2.23 |

Full results by tail/head arity and score are in `metric_summary_by_arity.csv`.
