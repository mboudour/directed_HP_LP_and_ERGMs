# Native-event directed hard-negative benchmark

- Dataset: `enron_20150507`
- Each panel is balanced with a held-out native-event type and one structurally constructed, unseen hard negative. Scores are uncalibrated ranking rules.
- Reversal/orientation changes tail and head roles. Role exchange preserves both tail and head arities while swapping one actor across roles.

## Panel coverage

| Mechanism | Replicate | Candidate-eligible positives | Reversal pairs | Role-exchange pairs |
|---|---:|---:|---:|---:|
| mcar | 1 | 197 | 86 | 82 |
| mcar | 2 | 198 | 96 | 90 |
| mcar | 3 | 211 | 94 | 88 |
| mnar_out | 1 | 224 | 95 | 81 |
| mnar_out | 2 | 194 | 90 | 82 |
| mnar_out | 3 | 203 | 96 | 89 |

## Ranking metrics across completed replicates

| Panel | Mechanism | Score | Metric | Replicates | Mean | SD |
|---|---|---|---|---:|---:|---:|
| reversal_orientation | mcar | already_observed_footprint | pr_auc | 3 | 0.5311 | 0.0103 |
| reversal_orientation | mcar | already_observed_footprint | precision_at_k | 3 | 0.5378 | 0.0096 |
| reversal_orientation | mcar | already_observed_footprint | recall_at_k | 3 | 0.5378 | 0.0096 |
| reversal_orientation | mcar | already_observed_footprint | roc_auc | 3 | 0.5524 | 0.0147 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.5227 | 0.0385 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.5065 | 0.0305 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.5065 | 0.0305 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.5121 | 0.0514 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.5112 | 0.0131 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.4980 | 0.0110 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.4980 | 0.0110 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.5023 | 0.0192 |
| reversal_orientation | mcar | lifted_cn_total_mean | pr_auc | 3 | 0.5142 | 0.0124 |
| reversal_orientation | mcar | lifted_cn_total_mean | precision_at_k | 3 | 0.5109 | 0.0142 |
| reversal_orientation | mcar | lifted_cn_total_mean | recall_at_k | 3 | 0.5109 | 0.0142 |
| reversal_orientation | mcar | lifted_cn_total_mean | roc_auc | 3 | 0.5064 | 0.0187 |
| reversal_orientation | mcar | lifted_degree_product_mean | pr_auc | 3 | 0.5707 | 0.0101 |
| reversal_orientation | mcar | lifted_degree_product_mean | precision_at_k | 3 | 0.5599 | 0.0132 |
| reversal_orientation | mcar | lifted_degree_product_mean | recall_at_k | 3 | 0.5599 | 0.0132 |
| reversal_orientation | mcar | lifted_degree_product_mean | roc_auc | 3 | 0.5667 | 0.0154 |
| reversal_orientation | mcar | lifted_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oi_mean | pr_auc | 3 | 0.5183 | 0.0263 |
| reversal_orientation | mcar | lifted_oi_mean | precision_at_k | 3 | 0.5107 | 0.0299 |
| reversal_orientation | mcar | lifted_oi_mean | recall_at_k | 3 | 0.5107 | 0.0299 |
| reversal_orientation | mcar | lifted_oi_mean | roc_auc | 3 | 0.5134 | 0.0445 |
| reversal_orientation | mcar | lifted_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | pr_auc | 3 | 0.4706 | 0.0048 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | precision_at_k | 3 | 0.4615 | 0.0092 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | recall_at_k | 3 | 0.4615 | 0.0092 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | roc_auc | 3 | 0.4465 | 0.0043 |
| reversal_orientation | mnar_out | already_observed_footprint | pr_auc | 3 | 0.4703 | 0.0029 |
| reversal_orientation | mnar_out | already_observed_footprint | precision_at_k | 3 | 0.4384 | 0.0124 |
| reversal_orientation | mnar_out | already_observed_footprint | recall_at_k | 3 | 0.4384 | 0.0124 |
| reversal_orientation | mnar_out | already_observed_footprint | roc_auc | 3 | 0.4114 | 0.0190 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.4233 | 0.0177 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.4112 | 0.0484 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.4112 | 0.0484 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.3615 | 0.0353 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.4692 | 0.0103 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.4521 | 0.0235 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.4521 | 0.0235 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.4504 | 0.0192 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | pr_auc | 3 | 0.4600 | 0.0120 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | precision_at_k | 3 | 0.4412 | 0.0293 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | recall_at_k | 3 | 0.4412 | 0.0293 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | roc_auc | 3 | 0.4393 | 0.0226 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | pr_auc | 3 | 0.4311 | 0.0354 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | precision_at_k | 3 | 0.3975 | 0.0305 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | recall_at_k | 3 | 0.3975 | 0.0305 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | roc_auc | 3 | 0.3404 | 0.0254 |
| reversal_orientation | mnar_out | lifted_ii_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oi_mean | pr_auc | 3 | 0.4316 | 0.0150 |
| reversal_orientation | mnar_out | lifted_oi_mean | precision_at_k | 3 | 0.4138 | 0.0362 |
| reversal_orientation | mnar_out | lifted_oi_mean | recall_at_k | 3 | 0.4138 | 0.0362 |
| reversal_orientation | mnar_out | lifted_oi_mean | roc_auc | 3 | 0.3658 | 0.0356 |
| reversal_orientation | mnar_out | lifted_oo_mean | pr_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | precision_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | recall_at_k | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | roc_auc | 3 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | pr_auc | 3 | 0.5823 | 0.0188 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | precision_at_k | 3 | 0.5952 | 0.0043 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | recall_at_k | 3 | 0.5952 | 0.0043 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | roc_auc | 3 | 0.6147 | 0.0133 |
| role_exchange | mcar | already_observed_footprint | pr_auc | 3 | 0.5466 | 0.0155 |
| role_exchange | mcar | already_observed_footprint | precision_at_k | 3 | 0.5498 | 0.0150 |
| role_exchange | mcar | already_observed_footprint | recall_at_k | 3 | 0.5498 | 0.0150 |
| role_exchange | mcar | already_observed_footprint | roc_auc | 3 | 0.5724 | 0.0205 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5053 | 0.0033 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.4884 | 0.0151 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.4884 | 0.0151 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.4830 | 0.0114 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.5249 | 0.0439 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.5047 | 0.0489 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.5047 | 0.0489 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.5135 | 0.0586 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.5075 | 0.0115 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.5020 | 0.0216 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.5020 | 0.0216 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.4994 | 0.0144 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.5156 | 0.0160 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.4996 | 0.0196 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.4996 | 0.0196 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.4960 | 0.0263 |
| role_exchange | mcar | lifted_cn_total_mean | pr_auc | 3 | 0.5178 | 0.0202 |
| role_exchange | mcar | lifted_cn_total_mean | precision_at_k | 3 | 0.5057 | 0.0272 |
| role_exchange | mcar | lifted_cn_total_mean | recall_at_k | 3 | 0.5057 | 0.0272 |
| role_exchange | mcar | lifted_cn_total_mean | roc_auc | 3 | 0.4999 | 0.0267 |
| role_exchange | mcar | lifted_degree_product_mean | pr_auc | 3 | 0.5762 | 0.0146 |
| role_exchange | mcar | lifted_degree_product_mean | precision_at_k | 3 | 0.5730 | 0.0160 |
| role_exchange | mcar | lifted_degree_product_mean | recall_at_k | 3 | 0.5730 | 0.0160 |
| role_exchange | mcar | lifted_degree_product_mean | roc_auc | 3 | 0.5779 | 0.0146 |
| role_exchange | mcar | lifted_ii_mean | pr_auc | 3 | 0.5037 | 0.0067 |
| role_exchange | mcar | lifted_ii_mean | precision_at_k | 3 | 0.4893 | 0.0151 |
| role_exchange | mcar | lifted_ii_mean | recall_at_k | 3 | 0.4893 | 0.0151 |
| role_exchange | mcar | lifted_ii_mean | roc_auc | 3 | 0.4871 | 0.0076 |
| role_exchange | mcar | lifted_oi_mean | pr_auc | 3 | 0.5210 | 0.0367 |
| role_exchange | mcar | lifted_oi_mean | precision_at_k | 3 | 0.5004 | 0.0288 |
| role_exchange | mcar | lifted_oi_mean | recall_at_k | 3 | 0.5004 | 0.0288 |
| role_exchange | mcar | lifted_oi_mean | roc_auc | 3 | 0.5133 | 0.0495 |
| role_exchange | mcar | lifted_oo_mean | pr_auc | 3 | 0.5065 | 0.0083 |
| role_exchange | mcar | lifted_oo_mean | precision_at_k | 3 | 0.4998 | 0.0159 |
| role_exchange | mcar | lifted_oo_mean | recall_at_k | 3 | 0.4998 | 0.0159 |
| role_exchange | mcar | lifted_oo_mean | roc_auc | 3 | 0.5005 | 0.0117 |
| role_exchange | mcar | lifted_reverse_arc_mean | pr_auc | 3 | 0.4719 | 0.0069 |
| role_exchange | mcar | lifted_reverse_arc_mean | precision_at_k | 3 | 0.4599 | 0.0117 |
| role_exchange | mcar | lifted_reverse_arc_mean | recall_at_k | 3 | 0.4599 | 0.0117 |
| role_exchange | mcar | lifted_reverse_arc_mean | roc_auc | 3 | 0.4455 | 0.0026 |
| role_exchange | mnar_out | already_observed_footprint | pr_auc | 3 | 0.4766 | 0.0072 |
| role_exchange | mnar_out | already_observed_footprint | precision_at_k | 3 | 0.4558 | 0.0208 |
| role_exchange | mnar_out | already_observed_footprint | recall_at_k | 3 | 0.4558 | 0.0208 |
| role_exchange | mnar_out | already_observed_footprint | roc_auc | 3 | 0.4341 | 0.0293 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 3 | 0.5515 | 0.0086 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 3 | 0.5310 | 0.0075 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 3 | 0.5310 | 0.0075 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 3 | 0.5408 | 0.0068 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 3 | 0.4445 | 0.0187 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 3 | 0.4161 | 0.0301 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 3 | 0.4161 | 0.0301 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 3 | 0.3879 | 0.0274 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 3 | 0.4920 | 0.0114 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 3 | 0.4693 | 0.0267 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 3 | 0.4693 | 0.0267 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 3 | 0.4572 | 0.0075 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 3 | 0.4887 | 0.0120 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 3 | 0.4798 | 0.0156 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 3 | 0.4798 | 0.0156 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 3 | 0.4707 | 0.0042 |
| role_exchange | mnar_out | lifted_cn_total_mean | pr_auc | 3 | 0.4799 | 0.0139 |
| role_exchange | mnar_out | lifted_cn_total_mean | precision_at_k | 3 | 0.4492 | 0.0118 |
| role_exchange | mnar_out | lifted_cn_total_mean | recall_at_k | 3 | 0.4492 | 0.0118 |
| role_exchange | mnar_out | lifted_cn_total_mean | roc_auc | 3 | 0.4548 | 0.0110 |
| role_exchange | mnar_out | lifted_degree_product_mean | pr_auc | 3 | 0.4630 | 0.0508 |
| role_exchange | mnar_out | lifted_degree_product_mean | precision_at_k | 3 | 0.4036 | 0.0253 |
| role_exchange | mnar_out | lifted_degree_product_mean | recall_at_k | 3 | 0.4036 | 0.0253 |
| role_exchange | mnar_out | lifted_degree_product_mean | roc_auc | 3 | 0.3688 | 0.0392 |
| role_exchange | mnar_out | lifted_ii_mean | pr_auc | 3 | 0.5442 | 0.0081 |
| role_exchange | mnar_out | lifted_ii_mean | precision_at_k | 3 | 0.5219 | 0.0084 |
| role_exchange | mnar_out | lifted_ii_mean | recall_at_k | 3 | 0.5219 | 0.0084 |
| role_exchange | mnar_out | lifted_ii_mean | roc_auc | 3 | 0.5384 | 0.0039 |
| role_exchange | mnar_out | lifted_oi_mean | pr_auc | 3 | 0.4462 | 0.0153 |
| role_exchange | mnar_out | lifted_oi_mean | precision_at_k | 3 | 0.4181 | 0.0083 |
| role_exchange | mnar_out | lifted_oi_mean | recall_at_k | 3 | 0.4181 | 0.0083 |
| role_exchange | mnar_out | lifted_oi_mean | roc_auc | 3 | 0.3903 | 0.0264 |
| role_exchange | mnar_out | lifted_oo_mean | pr_auc | 3 | 0.4866 | 0.0107 |
| role_exchange | mnar_out | lifted_oo_mean | precision_at_k | 3 | 0.4675 | 0.0095 |
| role_exchange | mnar_out | lifted_oo_mean | recall_at_k | 3 | 0.4675 | 0.0095 |
| role_exchange | mnar_out | lifted_oo_mean | roc_auc | 3 | 0.4539 | 0.0056 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | pr_auc | 3 | 0.5497 | 0.0032 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | precision_at_k | 3 | 0.5342 | 0.0186 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | recall_at_k | 3 | 0.5342 | 0.0186 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | roc_auc | 3 | 0.5571 | 0.0083 |

The `already_observed_footprint` column is a diagnostic baseline, not a prediction model. A valid hard negative must not be any known native event type, so an unavailable reversal or role exchange is recorded as a coverage limitation rather than relabelled.
