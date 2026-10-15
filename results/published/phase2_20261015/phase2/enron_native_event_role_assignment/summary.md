# Native-event role-assignment evaluation

- Dataset: `enron_20150507`
- Target: assign the known participants of each held-out event to its fixed tail/head arities.
- Candidate set: every compatible partition; no random case-control prevalence is implied.
- Metrics use uniform tie-breaking expectations and are reported overall through arity rows.

## Split coverage

| Mechanism | Replicate | Held-out types | Evaluated types | Mean partitions |
|---|---:|---:|---:|---:|
| mcar | 1 | 215 | 215 | 2.15 |
| mcar | 2 | 215 | 215 | 2.19 |
| mcar | 3 | 215 | 215 | 2.14 |
| mnar_out | 1 | 231 | 231 | 2.21 |
| mnar_out | 2 | 210 | 210 | 2.19 |
| mnar_out | 3 | 208 | 208 | 2.23 |

Full results by tail/head arity and score are in `metric_summary_by_arity.csv`.
