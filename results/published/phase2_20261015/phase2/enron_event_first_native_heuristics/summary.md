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
| mcar | 4 | 215 | 206 | 206 |
| mcar | 5 | 215 | 200 | 200 |
| mcar | 6 | 215 | 196 | 196 |
| mcar | 7 | 215 | 211 | 211 |
| mcar | 8 | 215 | 206 | 206 |
| mcar | 9 | 215 | 201 | 201 |
| mcar | 10 | 215 | 201 | 201 |
| mcar | 11 | 215 | 196 | 196 |
| mcar | 12 | 215 | 196 | 196 |
| mcar | 13 | 215 | 195 | 195 |
| mcar | 14 | 215 | 187 | 187 |
| mcar | 15 | 215 | 208 | 208 |
| mcar | 16 | 215 | 205 | 205 |
| mcar | 17 | 215 | 202 | 202 |
| mcar | 18 | 215 | 204 | 204 |
| mcar | 19 | 215 | 196 | 196 |
| mcar | 20 | 215 | 198 | 198 |
| mcar | 21 | 215 | 206 | 206 |
| mcar | 22 | 215 | 201 | 201 |
| mcar | 23 | 215 | 205 | 205 |
| mcar | 24 | 215 | 204 | 204 |
| mcar | 25 | 215 | 200 | 200 |
| mcar | 26 | 215 | 207 | 207 |
| mcar | 27 | 215 | 201 | 201 |
| mcar | 28 | 215 | 206 | 206 |
| mcar | 29 | 215 | 199 | 199 |
| mcar | 30 | 215 | 200 | 200 |
| mnar_out | 1 | 231 | 224 | 224 |
| mnar_out | 2 | 210 | 194 | 194 |
| mnar_out | 3 | 208 | 203 | 203 |
| mnar_out | 4 | 228 | 213 | 213 |
| mnar_out | 5 | 213 | 202 | 202 |
| mnar_out | 6 | 217 | 207 | 207 |
| mnar_out | 7 | 209 | 199 | 199 |
| mnar_out | 8 | 212 | 202 | 202 |
| mnar_out | 9 | 222 | 211 | 211 |
| mnar_out | 10 | 209 | 197 | 197 |
| mnar_out | 11 | 204 | 191 | 191 |
| mnar_out | 12 | 222 | 207 | 207 |
| mnar_out | 13 | 212 | 197 | 197 |
| mnar_out | 14 | 213 | 202 | 202 |
| mnar_out | 15 | 213 | 199 | 199 |
| mnar_out | 16 | 217 | 206 | 206 |
| mnar_out | 17 | 202 | 186 | 186 |
| mnar_out | 18 | 227 | 215 | 215 |
| mnar_out | 19 | 222 | 214 | 214 |
| mnar_out | 20 | 217 | 213 | 213 |
| mnar_out | 21 | 200 | 193 | 193 |
| mnar_out | 22 | 211 | 200 | 200 |
| mnar_out | 23 | 218 | 201 | 201 |
| mnar_out | 24 | 216 | 210 | 210 |
| mnar_out | 25 | 219 | 210 | 210 |
| mnar_out | 26 | 207 | 197 | 197 |
| mnar_out | 27 | 212 | 200 | 200 |
| mnar_out | 28 | 210 | 197 | 197 |
| mnar_out | 29 | 228 | 218 | 218 |
| mnar_out | 30 | 220 | 213 | 213 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Completed replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 30 | 0.6279 | 0.0220 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.5799 | 0.0130 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.5799 | 0.0130 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.6352 | 0.0199 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.7476 | 0.0205 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6706 | 0.0227 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6706 | 0.0227 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7211 | 0.0212 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7538 | 0.0234 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.6731 | 0.0250 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.6731 | 0.0250 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7263 | 0.0242 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.7496 | 0.0287 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6703 | 0.0270 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6703 | 0.0270 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.7216 | 0.0277 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7966 | 0.0187 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.7107 | 0.0240 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.7107 | 0.0240 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7631 | 0.0181 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.7695 | 0.0196 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6979 | 0.0206 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6979 | 0.0206 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.7510 | 0.0188 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.5758 | 0.0276 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.5690 | 0.0213 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.5690 | 0.0213 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.5849 | 0.0288 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.7024 | 0.0191 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.6494 | 0.0155 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.6494 | 0.0155 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.7073 | 0.0195 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.7164 | 0.0212 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.6535 | 0.0202 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.6535 | 0.0202 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.7168 | 0.0233 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.7117 | 0.0262 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.6482 | 0.0218 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.6482 | 0.0218 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.7095 | 0.0267 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.7501 | 0.0186 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.7071 | 0.0155 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.7071 | 0.0155 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.7711 | 0.0154 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.5816 | 0.0175 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5506 | 0.0104 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5506 | 0.0104 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.5897 | 0.0170 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.7984 | 0.0204 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.7213 | 0.0216 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.7213 | 0.0216 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7790 | 0.0198 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.6545 | 0.0226 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.5470 | 0.0232 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.5470 | 0.0232 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.5828 | 0.0201 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.6383 | 0.0235 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5288 | 0.0292 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5288 | 0.0292 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5587 | 0.0251 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7472 | 0.0206 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.6602 | 0.0244 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.6602 | 0.0244 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7193 | 0.0218 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.7021 | 0.0218 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.6335 | 0.0217 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.6335 | 0.0217 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.6845 | 0.0236 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.5125 | 0.0257 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.4842 | 0.0289 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.4842 | 0.0289 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.4548 | 0.0262 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.7516 | 0.0192 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.6943 | 0.0196 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.6943 | 0.0196 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.7613 | 0.0196 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.6168 | 0.0221 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.5325 | 0.0192 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.5325 | 0.0192 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.5695 | 0.0213 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.6039 | 0.0248 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.5102 | 0.0253 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.5102 | 0.0253 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.5441 | 0.0273 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.7761 | 0.0177 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.7362 | 0.0173 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.7362 | 0.0173 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.7968 | 0.0160 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
