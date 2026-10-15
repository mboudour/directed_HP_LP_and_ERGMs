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
| mcar | 4 | 215 | 215 | 2.14 |
| mcar | 5 | 215 | 215 | 2.15 |
| mcar | 6 | 215 | 215 | 2.12 |
| mcar | 7 | 215 | 215 | 2.17 |
| mcar | 8 | 215 | 215 | 2.16 |
| mcar | 9 | 215 | 215 | 2.17 |
| mcar | 10 | 215 | 215 | 2.13 |
| mcar | 11 | 215 | 215 | 2.17 |
| mcar | 12 | 215 | 215 | 2.11 |
| mcar | 13 | 215 | 215 | 2.11 |
| mcar | 14 | 215 | 215 | 2.09 |
| mcar | 15 | 215 | 215 | 2.20 |
| mcar | 16 | 215 | 215 | 2.16 |
| mcar | 17 | 215 | 215 | 2.14 |
| mcar | 18 | 215 | 215 | 2.13 |
| mcar | 19 | 215 | 215 | 2.13 |
| mcar | 20 | 215 | 215 | 2.16 |
| mcar | 21 | 215 | 215 | 2.18 |
| mcar | 22 | 215 | 215 | 2.13 |
| mcar | 23 | 215 | 215 | 2.16 |
| mcar | 24 | 215 | 215 | 2.19 |
| mcar | 25 | 215 | 215 | 2.14 |
| mcar | 26 | 215 | 215 | 2.15 |
| mcar | 27 | 215 | 215 | 2.12 |
| mcar | 28 | 215 | 215 | 2.15 |
| mcar | 29 | 215 | 215 | 2.18 |
| mcar | 30 | 215 | 215 | 2.13 |
| mnar_out | 1 | 231 | 231 | 2.21 |
| mnar_out | 2 | 210 | 210 | 2.19 |
| mnar_out | 3 | 208 | 208 | 2.23 |
| mnar_out | 4 | 228 | 228 | 2.20 |
| mnar_out | 5 | 213 | 213 | 2.21 |
| mnar_out | 6 | 217 | 217 | 2.21 |
| mnar_out | 7 | 209 | 209 | 2.20 |
| mnar_out | 8 | 212 | 212 | 2.23 |
| mnar_out | 9 | 222 | 222 | 2.23 |
| mnar_out | 10 | 209 | 209 | 2.17 |
| mnar_out | 11 | 204 | 204 | 2.22 |
| mnar_out | 12 | 222 | 222 | 2.20 |
| mnar_out | 13 | 212 | 212 | 2.22 |
| mnar_out | 14 | 213 | 213 | 2.21 |
| mnar_out | 15 | 213 | 213 | 2.20 |
| mnar_out | 16 | 217 | 217 | 2.24 |
| mnar_out | 17 | 202 | 202 | 2.21 |
| mnar_out | 18 | 227 | 227 | 2.21 |
| mnar_out | 19 | 222 | 222 | 2.23 |
| mnar_out | 20 | 217 | 217 | 2.22 |
| mnar_out | 21 | 200 | 200 | 2.23 |
| mnar_out | 22 | 211 | 211 | 2.21 |
| mnar_out | 23 | 218 | 218 | 2.23 |
| mnar_out | 24 | 216 | 216 | 2.24 |
| mnar_out | 25 | 219 | 219 | 2.22 |
| mnar_out | 26 | 207 | 207 | 2.21 |
| mnar_out | 27 | 212 | 212 | 2.22 |
| mnar_out | 28 | 210 | 210 | 2.19 |
| mnar_out | 29 | 228 | 228 | 2.19 |
| mnar_out | 30 | 220 | 220 | 2.21 |

Full results by tail/head arity and score are in `metric_summary_by_arity.csv`.
