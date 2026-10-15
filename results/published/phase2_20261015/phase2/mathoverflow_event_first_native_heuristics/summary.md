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
| mcar | 4 | 321 | 314 | 314 |
| mcar | 5 | 321 | 307 | 307 |
| mcar | 6 | 321 | 305 | 305 |
| mcar | 7 | 321 | 310 | 310 |
| mcar | 8 | 321 | 308 | 308 |
| mcar | 9 | 321 | 304 | 304 |
| mcar | 10 | 321 | 302 | 302 |
| mcar | 11 | 321 | 309 | 309 |
| mcar | 12 | 321 | 311 | 311 |
| mcar | 13 | 321 | 299 | 299 |
| mcar | 14 | 321 | 313 | 313 |
| mcar | 15 | 321 | 301 | 301 |
| mcar | 16 | 321 | 305 | 305 |
| mcar | 17 | 321 | 304 | 304 |
| mcar | 18 | 321 | 310 | 310 |
| mcar | 19 | 321 | 312 | 312 |
| mcar | 20 | 321 | 308 | 308 |
| mcar | 21 | 321 | 312 | 312 |
| mcar | 22 | 321 | 302 | 302 |
| mcar | 23 | 321 | 312 | 312 |
| mcar | 24 | 321 | 308 | 308 |
| mcar | 25 | 321 | 308 | 308 |
| mcar | 26 | 321 | 311 | 311 |
| mcar | 27 | 321 | 306 | 306 |
| mcar | 28 | 321 | 310 | 310 |
| mcar | 29 | 321 | 302 | 302 |
| mcar | 30 | 321 | 305 | 305 |
| mnar_out | 1 | 330 | 318 | 318 |
| mnar_out | 2 | 314 | 309 | 309 |
| mnar_out | 3 | 310 | 292 | 292 |
| mnar_out | 4 | 318 | 312 | 312 |
| mnar_out | 5 | 335 | 322 | 322 |
| mnar_out | 6 | 329 | 314 | 314 |
| mnar_out | 7 | 298 | 288 | 288 |
| mnar_out | 8 | 320 | 311 | 311 |
| mnar_out | 9 | 317 | 316 | 316 |
| mnar_out | 10 | 303 | 296 | 296 |
| mnar_out | 11 | 321 | 310 | 310 |
| mnar_out | 12 | 305 | 301 | 301 |
| mnar_out | 13 | 340 | 327 | 327 |
| mnar_out | 14 | 321 | 311 | 311 |
| mnar_out | 15 | 304 | 300 | 300 |
| mnar_out | 16 | 321 | 312 | 312 |
| mnar_out | 17 | 311 | 309 | 309 |
| mnar_out | 18 | 333 | 325 | 325 |
| mnar_out | 19 | 324 | 313 | 313 |
| mnar_out | 20 | 320 | 311 | 311 |
| mnar_out | 21 | 314 | 306 | 306 |
| mnar_out | 22 | 318 | 308 | 308 |
| mnar_out | 23 | 322 | 312 | 312 |
| mnar_out | 24 | 324 | 315 | 315 |
| mnar_out | 25 | 332 | 329 | 329 |
| mnar_out | 26 | 324 | 320 | 320 |
| mnar_out | 27 | 335 | 317 | 317 |
| mnar_out | 28 | 305 | 299 | 299 |
| mnar_out | 29 | 354 | 337 | 337 |
| mnar_out | 30 | 324 | 317 | 317 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Completed replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 30 | 0.6050 | 0.0113 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.5649 | 0.0059 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.5649 | 0.0059 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.6127 | 0.0095 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.6584 | 0.0276 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6353 | 0.0175 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6353 | 0.0175 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.6691 | 0.0218 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7741 | 0.0126 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7104 | 0.0139 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7104 | 0.0139 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7662 | 0.0124 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5745 | 0.0249 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5336 | 0.0215 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5336 | 0.0215 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5416 | 0.0222 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7589 | 0.0237 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.7026 | 0.0152 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.7026 | 0.0152 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7655 | 0.0178 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.7459 | 0.0205 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6992 | 0.0142 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6992 | 0.0142 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.7621 | 0.0161 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.7868 | 0.0177 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.7170 | 0.0138 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.7170 | 0.0138 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.7907 | 0.0137 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.6442 | 0.0262 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.6339 | 0.0174 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.6339 | 0.0174 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.6652 | 0.0218 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.7511 | 0.0133 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.7049 | 0.0130 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.7049 | 0.0130 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.7621 | 0.0127 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.5525 | 0.0210 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.5226 | 0.0186 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.5226 | 0.0186 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.5311 | 0.0222 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.5207 | 0.0092 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.5197 | 0.0062 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.5197 | 0.0062 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.5334 | 0.0108 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.6071 | 0.0176 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5666 | 0.0106 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5666 | 0.0106 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.6150 | 0.0166 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.6826 | 0.0209 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6626 | 0.0210 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6626 | 0.0210 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.6976 | 0.0194 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7522 | 0.0216 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7081 | 0.0184 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7081 | 0.0184 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7567 | 0.0197 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5480 | 0.0178 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5202 | 0.0229 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5202 | 0.0229 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5149 | 0.0206 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7593 | 0.0218 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.7116 | 0.0142 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.7116 | 0.0142 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7724 | 0.0180 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.7442 | 0.0213 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.7061 | 0.0142 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.7061 | 0.0142 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.7682 | 0.0183 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.7763 | 0.0202 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.7072 | 0.0186 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.7072 | 0.0186 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.7845 | 0.0164 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.6710 | 0.0205 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.6614 | 0.0198 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.6614 | 0.0198 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.6953 | 0.0199 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.7309 | 0.0206 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.7035 | 0.0168 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.7035 | 0.0168 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.7524 | 0.0199 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.5292 | 0.0167 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.5148 | 0.0233 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.5148 | 0.0233 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.5081 | 0.0237 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.5219 | 0.0108 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.5207 | 0.0080 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.5207 | 0.0080 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.5349 | 0.0136 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
