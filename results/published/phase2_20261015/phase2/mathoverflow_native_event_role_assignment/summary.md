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
| mcar | 4 | 321 | 321 | 2.20 |
| mcar | 5 | 321 | 321 | 2.22 |
| mcar | 6 | 321 | 321 | 2.20 |
| mcar | 7 | 321 | 321 | 2.19 |
| mcar | 8 | 321 | 321 | 2.21 |
| mcar | 9 | 321 | 321 | 2.18 |
| mcar | 10 | 321 | 321 | 2.18 |
| mcar | 11 | 321 | 321 | 2.21 |
| mcar | 12 | 321 | 321 | 2.20 |
| mcar | 13 | 321 | 321 | 2.24 |
| mcar | 14 | 321 | 321 | 2.21 |
| mcar | 15 | 321 | 321 | 2.21 |
| mcar | 16 | 321 | 321 | 2.19 |
| mcar | 17 | 321 | 321 | 2.23 |
| mcar | 18 | 321 | 321 | 2.20 |
| mcar | 19 | 321 | 321 | 2.20 |
| mcar | 20 | 321 | 321 | 2.22 |
| mcar | 21 | 321 | 321 | 2.21 |
| mcar | 22 | 321 | 321 | 2.18 |
| mcar | 23 | 321 | 321 | 2.21 |
| mcar | 24 | 321 | 321 | 2.21 |
| mcar | 25 | 321 | 321 | 2.22 |
| mcar | 26 | 321 | 321 | 2.22 |
| mcar | 27 | 321 | 321 | 2.21 |
| mcar | 28 | 321 | 321 | 2.21 |
| mcar | 29 | 321 | 321 | 2.23 |
| mcar | 30 | 321 | 321 | 2.19 |
| mnar_out | 1 | 330 | 330 | 2.21 |
| mnar_out | 2 | 314 | 314 | 2.25 |
| mnar_out | 3 | 310 | 310 | 2.23 |
| mnar_out | 4 | 318 | 318 | 2.26 |
| mnar_out | 5 | 335 | 335 | 2.24 |
| mnar_out | 6 | 329 | 329 | 2.24 |
| mnar_out | 7 | 298 | 298 | 2.27 |
| mnar_out | 8 | 320 | 320 | 2.23 |
| mnar_out | 9 | 317 | 317 | 2.24 |
| mnar_out | 10 | 303 | 303 | 2.26 |
| mnar_out | 11 | 321 | 321 | 2.24 |
| mnar_out | 12 | 305 | 305 | 2.27 |
| mnar_out | 13 | 340 | 340 | 2.26 |
| mnar_out | 14 | 321 | 321 | 2.24 |
| mnar_out | 15 | 304 | 304 | 2.22 |
| mnar_out | 16 | 321 | 321 | 2.22 |
| mnar_out | 17 | 311 | 311 | 2.25 |
| mnar_out | 18 | 333 | 333 | 2.25 |
| mnar_out | 19 | 324 | 324 | 2.24 |
| mnar_out | 20 | 320 | 320 | 2.22 |
| mnar_out | 21 | 314 | 314 | 2.26 |
| mnar_out | 22 | 318 | 318 | 2.22 |
| mnar_out | 23 | 322 | 322 | 2.25 |
| mnar_out | 24 | 324 | 324 | 2.23 |
| mnar_out | 25 | 332 | 332 | 2.24 |
| mnar_out | 26 | 324 | 324 | 2.21 |
| mnar_out | 27 | 335 | 335 | 2.25 |
| mnar_out | 28 | 305 | 305 | 2.27 |
| mnar_out | 29 | 354 | 354 | 2.25 |
| mnar_out | 30 | 324 | 324 | 2.26 |

Full results by tail/head arity and score are in `metric_summary_by_arity.csv`.
