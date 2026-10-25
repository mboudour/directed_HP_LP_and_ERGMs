# Native-event role-assignment evaluation

- Dataset: `senate_118_s_bills_cap3_sensitivity`
- Target: assign the known participants of each held-out event to its fixed tail/head arities.
- Candidate set: every compatible partition; no random case-control prevalence is implied.
- Metrics use uniform tie-breaking expectations and are reported overall through arity rows.

## Split coverage

| Mechanism | Replicate | Held-out types | Evaluated types | Mean partitions |
|---|---:|---:|---:|---:|
| mcar | 1 | 672 | 672 | 2.51 |
| mcar | 2 | 672 | 672 | 2.53 |
| mcar | 3 | 672 | 672 | 2.50 |
| mcar | 4 | 672 | 672 | 2.50 |
| mcar | 5 | 672 | 672 | 2.54 |
| mcar | 6 | 672 | 672 | 2.49 |
| mcar | 7 | 672 | 672 | 2.47 |
| mcar | 8 | 672 | 672 | 2.53 |
| mcar | 9 | 672 | 672 | 2.51 |
| mcar | 10 | 672 | 672 | 2.51 |
| mcar | 11 | 672 | 672 | 2.54 |
| mcar | 12 | 672 | 672 | 2.49 |
| mcar | 13 | 672 | 672 | 2.52 |
| mcar | 14 | 672 | 672 | 2.50 |
| mcar | 15 | 672 | 672 | 2.53 |
| mcar | 16 | 672 | 672 | 2.51 |
| mcar | 17 | 672 | 672 | 2.50 |
| mcar | 18 | 672 | 672 | 2.49 |
| mcar | 19 | 672 | 672 | 2.55 |
| mcar | 20 | 672 | 672 | 2.52 |
| mcar | 21 | 672 | 672 | 2.51 |
| mcar | 22 | 672 | 672 | 2.47 |
| mcar | 23 | 672 | 672 | 2.55 |
| mcar | 24 | 672 | 672 | 2.51 |
| mcar | 25 | 672 | 672 | 2.50 |
| mcar | 26 | 672 | 672 | 2.52 |
| mcar | 27 | 672 | 672 | 2.51 |
| mcar | 28 | 672 | 672 | 2.50 |
| mcar | 29 | 672 | 672 | 2.50 |
| mcar | 30 | 672 | 672 | 2.55 |
| mnar_out | 1 | 661 | 661 | 2.55 |
| mnar_out | 2 | 706 | 706 | 2.56 |
| mnar_out | 3 | 649 | 649 | 2.58 |
| mnar_out | 4 | 674 | 674 | 2.60 |
| mnar_out | 5 | 671 | 671 | 2.56 |
| mnar_out | 6 | 700 | 700 | 2.56 |
| mnar_out | 7 | 686 | 686 | 2.53 |
| mnar_out | 8 | 687 | 687 | 2.55 |
| mnar_out | 9 | 677 | 677 | 2.55 |
| mnar_out | 10 | 710 | 710 | 2.57 |
| mnar_out | 11 | 658 | 658 | 2.57 |
| mnar_out | 12 | 677 | 677 | 2.55 |
| mnar_out | 13 | 693 | 693 | 2.56 |
| mnar_out | 14 | 668 | 668 | 2.57 |
| mnar_out | 15 | 678 | 678 | 2.56 |
| mnar_out | 16 | 696 | 696 | 2.55 |
| mnar_out | 17 | 660 | 660 | 2.57 |
| mnar_out | 18 | 691 | 691 | 2.54 |
| mnar_out | 19 | 670 | 670 | 2.53 |
| mnar_out | 20 | 675 | 675 | 2.54 |
| mnar_out | 21 | 672 | 672 | 2.56 |
| mnar_out | 22 | 698 | 698 | 2.55 |
| mnar_out | 23 | 661 | 661 | 2.54 |
| mnar_out | 24 | 663 | 663 | 2.53 |
| mnar_out | 25 | 650 | 650 | 2.56 |
| mnar_out | 26 | 657 | 657 | 2.57 |
| mnar_out | 27 | 679 | 679 | 2.52 |
| mnar_out | 28 | 661 | 661 | 2.56 |
| mnar_out | 29 | 656 | 656 | 2.55 |
| mnar_out | 30 | 685 | 685 | 2.56 |

Full results by tail/head arity and score are in `metric_summary_by_arity.csv`.
