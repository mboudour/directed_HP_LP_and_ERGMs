# Table 03C Primary Native Role Assignment

Weighted top-1 role-assignment accuracy across the fixed arity strata. Candidate partitions preserve each event's known actor set and role arities.

| dataset | mechanism | method | event evaluations | top1 accuracy |
| --- | --- | --- | --- | --- |
| Enron strict custodian core | MCAR | Already-observed footprint | 6450 | 0.3377 |
| Enron strict custodian core | MCAR | Degree-product mean | 6450 | 0.4478 |
| Enron strict custodian core | MCAR | Directed Adamic-Adar total | 6450 | 0.4832 |
| Enron strict custodian core | MCAR | Reverse-arc mean | 6450 | 0.6012 |
| Enron strict custodian core | MNAR-out | Already-observed footprint | 6449 | 0.2722 |
| Enron strict custodian core | MNAR-out | Degree-product mean | 6449 | 0.3010 |
| Enron strict custodian core | MNAR-out | Directed Adamic-Adar total | 6449 | 0.3851 |
| Enron strict custodian core | MNAR-out | Reverse-arc mean | 6449 | 0.6541 |
| MathOverflow reconstructed core | MCAR | Already-observed footprint | 9630 | 0.5257 |
| MathOverflow reconstructed core | MCAR | Degree-product mean | 9630 | 0.7817 |
| MathOverflow reconstructed core | MCAR | Directed Adamic-Adar total | 9630 | 0.6972 |
| MathOverflow reconstructed core | MCAR | Reverse-arc mean | 9630 | 0.3907 |
| MathOverflow reconstructed core | MNAR-out | Already-observed footprint | 9626 | 0.5267 |
| MathOverflow reconstructed core | MNAR-out | Degree-product mean | 9626 | 0.7521 |
| MathOverflow reconstructed core | MNAR-out | Directed Adamic-Adar total | 9626 | 0.6831 |
| MathOverflow reconstructed core | MNAR-out | Reverse-arc mean | 9626 | 0.3753 |
