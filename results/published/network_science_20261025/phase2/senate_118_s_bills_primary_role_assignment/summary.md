# Native-event role-assignment evaluation

- Dataset: `senate_118_s_bills`
- Target: assign the known participants of each held-out event to its fixed tail/head arities.
- Candidate set: every compatible partition; no random case-control prevalence is implied.
- Metrics use uniform tie-breaking expectations and are reported overall through arity rows.

## Split coverage

| Mechanism | Replicate | Held-out types | Evaluated types | Mean partitions |
|---|---:|---:|---:|---:|
| mcar | 1 | 962 | 962 | 3.72 |
| mcar | 2 | 962 | 962 | 3.73 |
| mcar | 3 | 962 | 962 | 3.74 |
| mcar | 4 | 962 | 962 | 3.78 |
| mcar | 5 | 962 | 962 | 3.68 |
| mcar | 6 | 962 | 962 | 3.58 |
| mcar | 7 | 962 | 962 | 3.75 |
| mcar | 8 | 962 | 962 | 3.71 |
| mcar | 9 | 962 | 962 | 3.73 |
| mcar | 10 | 962 | 962 | 3.69 |
| mcar | 11 | 962 | 962 | 3.76 |
| mcar | 12 | 962 | 962 | 3.71 |
| mcar | 13 | 962 | 962 | 3.74 |
| mcar | 14 | 962 | 962 | 3.69 |
| mcar | 15 | 962 | 962 | 3.76 |
| mcar | 16 | 962 | 962 | 3.67 |
| mcar | 17 | 962 | 962 | 3.75 |
| mcar | 18 | 962 | 962 | 3.61 |
| mcar | 19 | 962 | 962 | 3.71 |
| mcar | 20 | 962 | 962 | 3.67 |
| mcar | 21 | 962 | 962 | 3.58 |
| mcar | 22 | 962 | 962 | 3.77 |
| mcar | 23 | 962 | 962 | 3.70 |
| mcar | 24 | 962 | 962 | 3.67 |
| mcar | 25 | 962 | 962 | 3.71 |
| mcar | 26 | 962 | 962 | 3.67 |
| mcar | 27 | 962 | 962 | 3.72 |
| mcar | 28 | 962 | 962 | 3.73 |
| mcar | 29 | 962 | 962 | 3.56 |
| mcar | 30 | 962 | 962 | 3.66 |
| mnar_out | 1 | 946 | 946 | 3.86 |
| mnar_out | 2 | 972 | 972 | 3.84 |
| mnar_out | 3 | 962 | 962 | 3.91 |
| mnar_out | 4 | 965 | 965 | 3.88 |
| mnar_out | 5 | 925 | 925 | 3.84 |
| mnar_out | 6 | 1024 | 1024 | 3.81 |
| mnar_out | 7 | 952 | 952 | 3.80 |
| mnar_out | 8 | 975 | 975 | 3.84 |
| mnar_out | 9 | 972 | 972 | 3.80 |
| mnar_out | 10 | 993 | 993 | 3.77 |
| mnar_out | 11 | 936 | 936 | 3.91 |
| mnar_out | 12 | 982 | 982 | 3.94 |
| mnar_out | 13 | 982 | 982 | 3.88 |
| mnar_out | 14 | 924 | 924 | 3.78 |
| mnar_out | 15 | 955 | 955 | 3.76 |
| mnar_out | 16 | 985 | 985 | 3.96 |
| mnar_out | 17 | 967 | 967 | 3.92 |
| mnar_out | 18 | 993 | 993 | 3.80 |
| mnar_out | 19 | 964 | 964 | 3.75 |
| mnar_out | 20 | 985 | 985 | 3.86 |
| mnar_out | 21 | 989 | 989 | 3.82 |
| mnar_out | 22 | 967 | 967 | 3.77 |
| mnar_out | 23 | 947 | 947 | 3.86 |
| mnar_out | 24 | 963 | 963 | 3.83 |
| mnar_out | 25 | 952 | 952 | 3.84 |
| mnar_out | 26 | 959 | 959 | 3.84 |
| mnar_out | 27 | 958 | 958 | 3.79 |
| mnar_out | 28 | 930 | 930 | 3.82 |
| mnar_out | 29 | 938 | 938 | 3.77 |
| mnar_out | 30 | 1001 | 1001 | 3.85 |

Full results by tail/head arity and score are in `metric_summary_by_arity.csv`.
