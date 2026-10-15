# Event-first native-event heuristic benchmark

- Dataset: `enron_20150507`
- Target: held-out native tail/head **event types**; duplicate records of a selected type were removed together before scoring.
- Candidate universe: participants are pairwise within weak distance two in the split's observed projection. Random negatives are matched exactly on tail/head arity and are not observed or held-out native event types.
- Scores are uncalibrated ranking rules. ROC-AUC, PR-AUC, precision@k, and recall@k are valid here; accuracy, F1, MCC, and log loss are intentionally omitted.

## Candidate-panel coverage

| Mechanism | Replicate | Held-out types | Positive types eligible for the candidate universe | Random negatives |
|---|---:|---:|---:|---:|
| mcar | 1 | 215 | 197 | 197 |
| mcar | 2 | 215 | 198 | 198 |
| mcar | 3 | 215 | 211 | 211 |
| mnar_out | 1 | 231 | 224 | 224 |
| mnar_out | 2 | 210 | 194 | 194 |
| mnar_out | 3 | 208 | 203 | 203 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Completed replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 3 | 0.6444 | 0.0090 |
| mcar | already_observed_footprint | precision_at_k | 3 | 0.5907 | 0.0066 |
| mcar | already_observed_footprint | recall_at_k | 3 | 0.5907 | 0.0066 |
| mcar | already_observed_footprint | roc_auc | 3 | 0.6511 | 0.0092 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.7514 | 0.0316 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.6802 | 0.0275 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.6802 | 0.0275 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.7318 | 0.0342 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.7531 | 0.0424 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.6683 | 0.0498 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.6683 | 0.0498 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.7178 | 0.0554 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.7651 | 0.0406 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.6899 | 0.0372 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.6899 | 0.0372 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.7390 | 0.0394 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.7988 | 0.0345 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.7234 | 0.0329 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.7234 | 0.0329 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.7752 | 0.0367 |
| mcar | lifted_cn_total_mean | pr_auc | 3 | 0.7718 | 0.0384 |
| mcar | lifted_cn_total_mean | precision_at_k | 3 | 0.7005 | 0.0360 |
| mcar | lifted_cn_total_mean | recall_at_k | 3 | 0.7005 | 0.0360 |
| mcar | lifted_cn_total_mean | roc_auc | 3 | 0.7575 | 0.0431 |
| mcar | lifted_degree_product_mean | pr_auc | 3 | 0.5630 | 0.0326 |
| mcar | lifted_degree_product_mean | precision_at_k | 3 | 0.5649 | 0.0317 |
| mcar | lifted_degree_product_mean | recall_at_k | 3 | 0.5649 | 0.0317 |
| mcar | lifted_degree_product_mean | roc_auc | 3 | 0.5792 | 0.0489 |
| mcar | lifted_ii_mean | pr_auc | 3 | 0.7080 | 0.0336 |
| mcar | lifted_ii_mean | precision_at_k | 3 | 0.6533 | 0.0296 |
| mcar | lifted_ii_mean | recall_at_k | 3 | 0.6533 | 0.0296 |
| mcar | lifted_ii_mean | roc_auc | 3 | 0.7135 | 0.0342 |
| mcar | lifted_oi_mean | pr_auc | 3 | 0.7165 | 0.0383 |
| mcar | lifted_oi_mean | precision_at_k | 3 | 0.6446 | 0.0454 |
| mcar | lifted_oi_mean | recall_at_k | 3 | 0.6446 | 0.0454 |
| mcar | lifted_oi_mean | roc_auc | 3 | 0.7080 | 0.0515 |
| mcar | lifted_oo_mean | pr_auc | 3 | 0.7193 | 0.0346 |
| mcar | lifted_oo_mean | precision_at_k | 3 | 0.6551 | 0.0354 |
| mcar | lifted_oo_mean | recall_at_k | 3 | 0.6551 | 0.0354 |
| mcar | lifted_oo_mean | roc_auc | 3 | 0.7191 | 0.0398 |
| mcar | lifted_reverse_arc_mean | pr_auc | 3 | 0.7589 | 0.0088 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 3 | 0.7158 | 0.0029 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 3 | 0.7158 | 0.0029 |
| mcar | lifted_reverse_arc_mean | roc_auc | 3 | 0.7800 | 0.0049 |
| mnar_out | already_observed_footprint | pr_auc | 3 | 0.5677 | 0.0243 |
| mnar_out | already_observed_footprint | precision_at_k | 3 | 0.5445 | 0.0160 |
| mnar_out | already_observed_footprint | recall_at_k | 3 | 0.5445 | 0.0160 |
| mnar_out | already_observed_footprint | roc_auc | 3 | 0.5786 | 0.0258 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.7854 | 0.0286 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.7148 | 0.0281 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.7148 | 0.0281 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.7707 | 0.0200 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.6502 | 0.0024 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.5511 | 0.0269 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.5511 | 0.0269 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.5871 | 0.0162 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.6338 | 0.0042 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5312 | 0.0065 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5312 | 0.0065 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.5624 | 0.0070 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.7502 | 0.0189 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.6628 | 0.0217 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.6628 | 0.0217 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.7279 | 0.0181 |
| mnar_out | lifted_cn_total_mean | pr_auc | 3 | 0.7111 | 0.0205 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 3 | 0.6451 | 0.0320 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 3 | 0.6451 | 0.0320 |
| mnar_out | lifted_cn_total_mean | roc_auc | 3 | 0.6997 | 0.0239 |
| mnar_out | lifted_degree_product_mean | pr_auc | 3 | 0.5134 | 0.0240 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 3 | 0.4868 | 0.0343 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 3 | 0.4868 | 0.0343 |
| mnar_out | lifted_degree_product_mean | roc_auc | 3 | 0.4579 | 0.0160 |
| mnar_out | lifted_ii_mean | pr_auc | 3 | 0.7469 | 0.0207 |
| mnar_out | lifted_ii_mean | precision_at_k | 3 | 0.6896 | 0.0152 |
| mnar_out | lifted_ii_mean | recall_at_k | 3 | 0.6896 | 0.0152 |
| mnar_out | lifted_ii_mean | roc_auc | 3 | 0.7553 | 0.0189 |
| mnar_out | lifted_oi_mean | pr_auc | 3 | 0.6152 | 0.0090 |
| mnar_out | lifted_oi_mean | precision_at_k | 3 | 0.5417 | 0.0211 |
| mnar_out | lifted_oi_mean | recall_at_k | 3 | 0.5417 | 0.0211 |
| mnar_out | lifted_oi_mean | roc_auc | 3 | 0.5764 | 0.0174 |
| mnar_out | lifted_oo_mean | pr_auc | 3 | 0.6017 | 0.0182 |
| mnar_out | lifted_oo_mean | precision_at_k | 3 | 0.5163 | 0.0083 |
| mnar_out | lifted_oo_mean | recall_at_k | 3 | 0.5163 | 0.0083 |
| mnar_out | lifted_oo_mean | roc_auc | 3 | 0.5505 | 0.0159 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 3 | 0.7884 | 0.0155 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 3 | 0.7474 | 0.0078 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 3 | 0.7474 | 0.0078 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 3 | 0.8078 | 0.0084 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
