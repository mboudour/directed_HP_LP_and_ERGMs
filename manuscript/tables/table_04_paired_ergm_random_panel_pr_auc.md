# Table 04 Paired Ergm Random Panel Pr Auc

Predeclared paired random-panel contrast. Bootstrap and sign-flip calculations resample whole frozen masks within dataset only.

| dataset | mechanism | contrast | paired masks | mean difference | bootstrap ci low | bootstrap ci high | paired sign flip p value | bootstrap reps | permutation reps | p value resolution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Enron strict custodian core | MCAR | M4c::L1g − M0::L1 | 30 | 0.3584 | 0.3519 | 0.3648 | 5.00e-05 | 10000 | 20000 | 1 / 20,001 |
| Enron strict custodian core | MNAR-out | M4c::L1g − M0::L1 | 30 | 0.3324 | 0.3269 | 0.3379 | 5.00e-05 | 10000 | 20000 | 1 / 20,001 |
| MathOverflow reconstructed core | MCAR | M4c::L1g − M0::L1 | 30 | 0.2396 | 0.2305 | 0.2485 | 5.00e-05 | 10000 | 20000 | 1 / 20,001 |
| MathOverflow reconstructed core | MNAR-out | M4c::L1g − M0::L1 | 30 | 0.2394 | 0.2303 | 0.2484 | 5.00e-05 | 10000 | 20000 | 1 / 20,001 |
