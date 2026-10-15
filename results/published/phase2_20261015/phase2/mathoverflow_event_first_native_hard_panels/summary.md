# Native-event directed hard-negative benchmark

- Dataset: `mathoverflow_stackexchange_2024`
- Each panel is balanced with a held-out native-event type and one structurally constructed, unseen hard negative. Scores are uncalibrated ranking rules.
- Reversal/orientation changes tail and head roles. Role exchange preserves both tail and head arities while swapping one actor across roles.

## Panel coverage

| Mechanism | Replicate | Candidate-eligible positives | Reversal pairs | Role-exchange pairs |
|---|---:|---:|---:|---:|
| mcar | 1 | 311 | 278 | 277 |
| mcar | 2 | 309 | 277 | 277 |
| mcar | 3 | 312 | 288 | 288 |
| mnar_out | 1 | 318 | 290 | 289 |
| mnar_out | 2 | 309 | 276 | 276 |
| mnar_out | 3 | 292 | 269 | 269 |

## Ranking metrics across completed replicates

| Panel | Mechanism | Score | Metric | Replicates | Mean | SD |
|---|---|---|---|---:|---:|---:|
| reversal_orientation | mcar | already_observed_footprint | pr_auc | 3 | 0.5827 | 0.0077 |
| reversal_orientation | mcar | already_observed_footprint | precision_at_k | 3 | 0.5561 | 0.0032 |
| reversal_orientation | mcar | already_observed_footprint | recall_at_k | 3 | 0.5561 | 0.0032 |
| reversal_orientation | mcar | already_observed_footprint | roc_auc | 3 | 0.5967 | 0.0056 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.8122 | 0.0161 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.7511 | 0.0178 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.7511 | 0.0178 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.8053 | 0.0232 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.6150 | 0.0050 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.5848 | 0.0084 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.5848 | 0.0084 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.6225 | 0.0101 |
| reversal_orientation | mcar | lifted_cn_total_mean | pr_auc | 3 | 0.6306 | 0.0013 |
| reversal_orientation | mcar | lifted_cn_total_mean | precision_at_k | 3 | 0.5933 | 0.0072 |
| reversal_orientation | mcar | lifted_cn_total_mean | recall_at_k | 3 | 0.5933 | 0.0072 |
| reversal_orientation | mcar | lifted_cn_total_mean | roc_auc | 3 | 0.6419 | 0.0106 |
| reversal_orientation | mcar | lifted_degree_product_mean | pr_auc | 3 | 0.8782 | 0.0157 |
| reversal_orientation | mcar | lifted_degree_product_mean | precision_at_k | 3 | 0.7854 | 0.0157 |
| reversal_orientation | mcar | lifted_degree_product_mean | recall_at_k | 3 | 0.7854 | 0.0157 |
| reversal_orientation | mcar | lifted_degree_product_mean | roc_auc | 3 | 0.8719 | 0.0148 |
| reversal_orientation | mcar | lifted_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oi_mean | pr_auc | 3 | 0.7910 | 0.0167 |
| reversal_orientation | mcar | lifted_oi_mean | precision_at_k | 3 | 0.7393 | 0.0203 |
| reversal_orientation | mcar | lifted_oi_mean | recall_at_k | 3 | 0.7393 | 0.0203 |
| reversal_orientation | mcar | lifted_oi_mean | roc_auc | 3 | 0.8016 | 0.0226 |
| reversal_orientation | mcar | lifted_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | pr_auc | 3 | 0.4682 | 0.0027 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | precision_at_k | 3 | 0.4270 | 0.0053 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | recall_at_k | 3 | 0.4270 | 0.0053 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | roc_auc | 3 | 0.3805 | 0.0056 |
| reversal_orientation | mnar_out | already_observed_footprint | pr_auc | 3 | 0.5946 | 0.0132 |
| reversal_orientation | mnar_out | already_observed_footprint | precision_at_k | 3 | 0.5650 | 0.0100 |
| reversal_orientation | mnar_out | already_observed_footprint | recall_at_k | 3 | 0.5650 | 0.0100 |
| reversal_orientation | mnar_out | already_observed_footprint | roc_auc | 3 | 0.6099 | 0.0144 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.7683 | 0.0234 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.7281 | 0.0116 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.7281 | 0.0116 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.7710 | 0.0195 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.5938 | 0.0077 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.5738 | 0.0119 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.5738 | 0.0119 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.6082 | 0.0098 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | pr_auc | 3 | 0.6140 | 0.0092 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | precision_at_k | 3 | 0.5895 | 0.0071 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | recall_at_k | 3 | 0.5895 | 0.0071 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | roc_auc | 3 | 0.6321 | 0.0109 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | pr_auc | 3 | 0.8498 | 0.0287 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | precision_at_k | 3 | 0.7567 | 0.0301 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | recall_at_k | 3 | 0.7567 | 0.0301 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | roc_auc | 3 | 0.8460 | 0.0218 |
| reversal_orientation | mnar_out | lifted_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oi_mean | pr_auc | 3 | 0.7558 | 0.0215 |
| reversal_orientation | mnar_out | lifted_oi_mean | precision_at_k | 3 | 0.7231 | 0.0093 |
| reversal_orientation | mnar_out | lifted_oi_mean | recall_at_k | 3 | 0.7231 | 0.0093 |
| reversal_orientation | mnar_out | lifted_oi_mean | roc_auc | 3 | 0.7711 | 0.0201 |
| reversal_orientation | mnar_out | lifted_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | pr_auc | 3 | 0.4614 | 0.0011 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | precision_at_k | 3 | 0.4111 | 0.0073 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | recall_at_k | 3 | 0.4111 | 0.0073 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | roc_auc | 3 | 0.3599 | 0.0111 |
| role_exchange | mcar | already_observed_footprint | pr_auc | 3 | 0.5837 | 0.0070 |
| role_exchange | mcar | already_observed_footprint | precision_at_k | 3 | 0.5564 | 0.0032 |
| role_exchange | mcar | already_observed_footprint | recall_at_k | 3 | 0.5564 | 0.0032 |
| role_exchange | mcar | already_observed_footprint | roc_auc | 3 | 0.5975 | 0.0054 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5184 | 0.0007 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.5231 | 0.0064 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.5231 | 0.0064 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.5256 | 0.0052 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.8015 | 0.0141 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.7377 | 0.0122 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.7377 | 0.0122 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.7966 | 0.0205 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.4797 | 0.0019 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.4732 | 0.0052 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.4732 | 0.0052 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.4671 | 0.0035 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.6122 | 0.0011 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.5867 | 0.0079 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.5867 | 0.0079 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.6256 | 0.0075 |
| role_exchange | mcar | lifted_cn_total_mean | pr_auc | 3 | 0.6230 | 0.0038 |
| role_exchange | mcar | lifted_cn_total_mean | precision_at_k | 3 | 0.5980 | 0.0109 |
| role_exchange | mcar | lifted_cn_total_mean | recall_at_k | 3 | 0.5980 | 0.0109 |
| role_exchange | mcar | lifted_cn_total_mean | roc_auc | 3 | 0.6400 | 0.0087 |
| role_exchange | mcar | lifted_degree_product_mean | pr_auc | 3 | 0.8641 | 0.0158 |
| role_exchange | mcar | lifted_degree_product_mean | precision_at_k | 3 | 0.7737 | 0.0202 |
| role_exchange | mcar | lifted_degree_product_mean | recall_at_k | 3 | 0.7737 | 0.0202 |
| role_exchange | mcar | lifted_degree_product_mean | roc_auc | 3 | 0.8605 | 0.0162 |
| role_exchange | mcar | lifted_ii_mean | pr_auc | 3 | 0.5168 | 0.0016 |
| role_exchange | mcar | lifted_ii_mean | precision_at_k | 3 | 0.5216 | 0.0050 |
| role_exchange | mcar | lifted_ii_mean | recall_at_k | 3 | 0.5216 | 0.0050 |
| role_exchange | mcar | lifted_ii_mean | roc_auc | 3 | 0.5261 | 0.0043 |
| role_exchange | mcar | lifted_oi_mean | pr_auc | 3 | 0.7816 | 0.0153 |
| role_exchange | mcar | lifted_oi_mean | precision_at_k | 3 | 0.7259 | 0.0141 |
| role_exchange | mcar | lifted_oi_mean | recall_at_k | 3 | 0.7259 | 0.0141 |
| role_exchange | mcar | lifted_oi_mean | roc_auc | 3 | 0.7925 | 0.0195 |
| role_exchange | mcar | lifted_oo_mean | pr_auc | 3 | 0.4830 | 0.0015 |
| role_exchange | mcar | lifted_oo_mean | precision_at_k | 3 | 0.4761 | 0.0038 |
| role_exchange | mcar | lifted_oo_mean | recall_at_k | 3 | 0.4761 | 0.0038 |
| role_exchange | mcar | lifted_oo_mean | roc_auc | 3 | 0.4671 | 0.0029 |
| role_exchange | mcar | lifted_reverse_arc_mean | pr_auc | 3 | 0.4706 | 0.0028 |
| role_exchange | mcar | lifted_reverse_arc_mean | precision_at_k | 3 | 0.4301 | 0.0024 |
| role_exchange | mcar | lifted_reverse_arc_mean | recall_at_k | 3 | 0.4301 | 0.0024 |
| role_exchange | mcar | lifted_reverse_arc_mean | roc_auc | 3 | 0.3874 | 0.0027 |
| role_exchange | mnar_out | already_observed_footprint | pr_auc | 3 | 0.5863 | 0.0128 |
| role_exchange | mnar_out | already_observed_footprint | precision_at_k | 3 | 0.5619 | 0.0102 |
| role_exchange | mnar_out | already_observed_footprint | recall_at_k | 3 | 0.5619 | 0.0102 |
| role_exchange | mnar_out | already_observed_footprint | roc_auc | 3 | 0.6040 | 0.0146 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5348 | 0.0058 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.5272 | 0.0109 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.5272 | 0.0109 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.5363 | 0.0056 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.7570 | 0.0188 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.7189 | 0.0109 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.7189 | 0.0109 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.7632 | 0.0180 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.4820 | 0.0021 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.4807 | 0.0069 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.4807 | 0.0069 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.4681 | 0.0097 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.6134 | 0.0086 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.5899 | 0.0026 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.5899 | 0.0026 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.6254 | 0.0084 |
| role_exchange | mnar_out | lifted_cn_total_mean | pr_auc | 3 | 0.6231 | 0.0096 |
| role_exchange | mnar_out | lifted_cn_total_mean | precision_at_k | 3 | 0.6018 | 0.0058 |
| role_exchange | mnar_out | lifted_cn_total_mean | recall_at_k | 3 | 0.6018 | 0.0058 |
| role_exchange | mnar_out | lifted_cn_total_mean | roc_auc | 3 | 0.6435 | 0.0107 |
| role_exchange | mnar_out | lifted_degree_product_mean | pr_auc | 3 | 0.8309 | 0.0245 |
| role_exchange | mnar_out | lifted_degree_product_mean | precision_at_k | 3 | 0.7453 | 0.0287 |
| role_exchange | mnar_out | lifted_degree_product_mean | recall_at_k | 3 | 0.7453 | 0.0287 |
| role_exchange | mnar_out | lifted_degree_product_mean | roc_auc | 3 | 0.8321 | 0.0201 |
| role_exchange | mnar_out | lifted_ii_mean | pr_auc | 3 | 0.5314 | 0.0047 |
| role_exchange | mnar_out | lifted_ii_mean | precision_at_k | 3 | 0.5291 | 0.0079 |
| role_exchange | mnar_out | lifted_ii_mean | recall_at_k | 3 | 0.5291 | 0.0079 |
| role_exchange | mnar_out | lifted_ii_mean | roc_auc | 3 | 0.5373 | 0.0061 |
| role_exchange | mnar_out | lifted_oi_mean | pr_auc | 3 | 0.7441 | 0.0172 |
| role_exchange | mnar_out | lifted_oi_mean | precision_at_k | 3 | 0.7115 | 0.0044 |
| role_exchange | mnar_out | lifted_oi_mean | recall_at_k | 3 | 0.7115 | 0.0044 |
| role_exchange | mnar_out | lifted_oi_mean | roc_auc | 3 | 0.7628 | 0.0174 |
| role_exchange | mnar_out | lifted_oo_mean | pr_auc | 3 | 0.4818 | 0.0038 |
| role_exchange | mnar_out | lifted_oo_mean | precision_at_k | 3 | 0.4776 | 0.0097 |
| role_exchange | mnar_out | lifted_oo_mean | recall_at_k | 3 | 0.4776 | 0.0097 |
| role_exchange | mnar_out | lifted_oo_mean | roc_auc | 3 | 0.4659 | 0.0102 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | pr_auc | 3 | 0.4649 | 0.0011 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | precision_at_k | 3 | 0.4261 | 0.0035 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | recall_at_k | 3 | 0.4261 | 0.0035 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | roc_auc | 3 | 0.3829 | 0.0059 |

The `already_observed_footprint` column is a diagnostic baseline, not a prediction model. A valid hard negative must not be any known native event type, so an unavailable reversal or role exchange is recorded as a coverage limitation rather than relabelled.
