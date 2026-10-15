# Event-first native-event heuristic benchmark

- Dataset: `mathoverflow_stackexchange_2024`
- Target: held-out native tail/head **event types**; duplicate records of a selected type were removed together before scoring.
- Candidate universe: participants are pairwise within weak distance two in the split's observed projection. Random negatives are matched exactly on tail/head arity and are not observed or held-out native event types.
- Scores are uncalibrated ranking rules. ROC-AUC, PR-AUC, precision@k, and recall@k are valid here; accuracy, F1, MCC, and log loss are intentionally omitted.

## Candidate-panel coverage

| Mechanism | Replicate | Held-out types | Positive types eligible for the candidate universe | Random negatives |
|---|---:|---:|---:|---:|
| mcar | 1 | 321 | 311 | 311 |
| mcar | 2 | 321 | 309 | 309 |
| mcar | 3 | 321 | 312 | 312 |
| mnar_out | 1 | 330 | 318 | 318 |
| mnar_out | 2 | 314 | 309 | 309 |
| mnar_out | 3 | 310 | 292 | 292 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Completed replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 3 | 0.5966 | 0.0061 |
| mcar | already_observed_footprint | precision_at_k | 3 | 0.5606 | 0.0012 |
| mcar | already_observed_footprint | recall_at_k | 3 | 0.5606 | 0.0012 |
| mcar | already_observed_footprint | roc_auc | 3 | 0.6057 | 0.0028 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.6765 | 0.0283 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.6524 | 0.0140 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.6524 | 0.0140 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.6875 | 0.0226 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.7817 | 0.0168 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.7318 | 0.0089 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.7318 | 0.0089 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.7805 | 0.0151 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.5645 | 0.0134 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5225 | 0.0156 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5225 | 0.0156 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.5333 | 0.0175 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.7662 | 0.0238 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.7039 | 0.0268 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.7039 | 0.0268 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.7750 | 0.0243 |
| mcar | lifted_cn_total_mean | pr_auc | 3 | 0.7507 | 0.0188 |
| mcar | lifted_cn_total_mean | precision_at_k | 3 | 0.7022 | 0.0204 |
| mcar | lifted_cn_total_mean | recall_at_k | 3 | 0.7022 | 0.0204 |
| mcar | lifted_cn_total_mean | roc_auc | 3 | 0.7683 | 0.0200 |
| mcar | lifted_degree_product_mean | pr_auc | 3 | 0.7996 | 0.0158 |
| mcar | lifted_degree_product_mean | precision_at_k | 3 | 0.7249 | 0.0128 |
| mcar | lifted_degree_product_mean | recall_at_k | 3 | 0.7249 | 0.0128 |
| mcar | lifted_degree_product_mean | roc_auc | 3 | 0.8041 | 0.0181 |
| mcar | lifted_ii_mean | pr_auc | 3 | 0.6643 | 0.0228 |
| mcar | lifted_ii_mean | precision_at_k | 3 | 0.6509 | 0.0128 |
| mcar | lifted_ii_mean | recall_at_k | 3 | 0.6509 | 0.0128 |
| mcar | lifted_ii_mean | roc_auc | 3 | 0.6854 | 0.0214 |
| mcar | lifted_oi_mean | pr_auc | 3 | 0.7544 | 0.0168 |
| mcar | lifted_oi_mean | precision_at_k | 3 | 0.7094 | 0.0110 |
| mcar | lifted_oi_mean | recall_at_k | 3 | 0.7094 | 0.0110 |
| mcar | lifted_oi_mean | roc_auc | 3 | 0.7720 | 0.0152 |
| mcar | lifted_oo_mean | pr_auc | 3 | 0.5450 | 0.0099 |
| mcar | lifted_oo_mean | precision_at_k | 3 | 0.5153 | 0.0152 |
| mcar | lifted_oo_mean | recall_at_k | 3 | 0.5153 | 0.0152 |
| mcar | lifted_oo_mean | roc_auc | 3 | 0.5236 | 0.0170 |
| mcar | lifted_reverse_arc_mean | pr_auc | 3 | 0.5211 | 0.0108 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 3 | 0.5196 | 0.0076 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 3 | 0.5196 | 0.0076 |
| mcar | lifted_reverse_arc_mean | roc_auc | 3 | 0.5337 | 0.0132 |
| mnar_out | already_observed_footprint | pr_auc | 3 | 0.6167 | 0.0163 |
| mnar_out | already_observed_footprint | precision_at_k | 3 | 0.5714 | 0.0114 |
| mnar_out | already_observed_footprint | recall_at_k | 3 | 0.5714 | 0.0114 |
| mnar_out | already_observed_footprint | roc_auc | 3 | 0.6229 | 0.0167 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.6786 | 0.0256 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.6595 | 0.0297 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.6595 | 0.0297 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.6966 | 0.0262 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.7633 | 0.0371 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.7029 | 0.0417 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.7029 | 0.0417 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.7564 | 0.0401 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.5552 | 0.0096 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5236 | 0.0099 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5236 | 0.0099 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.5264 | 0.0154 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.7610 | 0.0241 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.7073 | 0.0157 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.7073 | 0.0157 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.7744 | 0.0214 |
| mnar_out | lifted_cn_total_mean | pr_auc | 3 | 0.7442 | 0.0240 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 3 | 0.7020 | 0.0142 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 3 | 0.7020 | 0.0142 |
| mnar_out | lifted_cn_total_mean | roc_auc | 3 | 0.7694 | 0.0215 |
| mnar_out | lifted_degree_product_mean | pr_auc | 3 | 0.7852 | 0.0388 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 3 | 0.7005 | 0.0318 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 3 | 0.7005 | 0.0318 |
| mnar_out | lifted_degree_product_mean | roc_auc | 3 | 0.7855 | 0.0312 |
| mnar_out | lifted_ii_mean | pr_auc | 3 | 0.6675 | 0.0267 |
| mnar_out | lifted_ii_mean | precision_at_k | 3 | 0.6572 | 0.0268 |
| mnar_out | lifted_ii_mean | recall_at_k | 3 | 0.6572 | 0.0268 |
| mnar_out | lifted_ii_mean | roc_auc | 3 | 0.6948 | 0.0275 |
| mnar_out | lifted_oi_mean | pr_auc | 3 | 0.7346 | 0.0372 |
| mnar_out | lifted_oi_mean | precision_at_k | 3 | 0.6896 | 0.0332 |
| mnar_out | lifted_oi_mean | recall_at_k | 3 | 0.6896 | 0.0332 |
| mnar_out | lifted_oi_mean | roc_auc | 3 | 0.7491 | 0.0404 |
| mnar_out | lifted_oo_mean | pr_auc | 3 | 0.5323 | 0.0123 |
| mnar_out | lifted_oo_mean | precision_at_k | 3 | 0.5196 | 0.0202 |
| mnar_out | lifted_oo_mean | recall_at_k | 3 | 0.5196 | 0.0202 |
| mnar_out | lifted_oo_mean | roc_auc | 3 | 0.5166 | 0.0213 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 3 | 0.5238 | 0.0043 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 3 | 0.5227 | 0.0028 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 3 | 0.5227 | 0.0028 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 3 | 0.5384 | 0.0051 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
