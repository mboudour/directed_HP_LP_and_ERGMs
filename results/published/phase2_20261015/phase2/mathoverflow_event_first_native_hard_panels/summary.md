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
| mcar | 4 | 314 | 282 | 282 |
| mcar | 5 | 307 | 279 | 279 |
| mcar | 6 | 305 | 273 | 273 |
| mcar | 7 | 310 | 282 | 281 |
| mcar | 8 | 308 | 288 | 288 |
| mcar | 9 | 304 | 279 | 279 |
| mcar | 10 | 302 | 271 | 271 |
| mcar | 11 | 309 | 281 | 280 |
| mcar | 12 | 311 | 277 | 277 |
| mcar | 13 | 299 | 270 | 270 |
| mcar | 14 | 313 | 284 | 284 |
| mcar | 15 | 301 | 270 | 270 |
| mcar | 16 | 305 | 275 | 275 |
| mcar | 17 | 304 | 274 | 272 |
| mcar | 18 | 310 | 280 | 280 |
| mcar | 19 | 312 | 286 | 286 |
| mcar | 20 | 308 | 272 | 272 |
| mcar | 21 | 312 | 283 | 283 |
| mcar | 22 | 302 | 273 | 272 |
| mcar | 23 | 312 | 276 | 276 |
| mcar | 24 | 308 | 279 | 279 |
| mcar | 25 | 308 | 272 | 272 |
| mcar | 26 | 311 | 284 | 284 |
| mcar | 27 | 306 | 269 | 269 |
| mcar | 28 | 310 | 287 | 286 |
| mcar | 29 | 302 | 274 | 273 |
| mcar | 30 | 305 | 271 | 271 |
| mnar_out | 1 | 318 | 290 | 289 |
| mnar_out | 2 | 309 | 276 | 276 |
| mnar_out | 3 | 292 | 269 | 269 |
| mnar_out | 4 | 312 | 283 | 283 |
| mnar_out | 5 | 322 | 297 | 297 |
| mnar_out | 6 | 314 | 285 | 284 |
| mnar_out | 7 | 288 | 264 | 263 |
| mnar_out | 8 | 311 | 281 | 281 |
| mnar_out | 9 | 316 | 286 | 285 |
| mnar_out | 10 | 296 | 268 | 268 |
| mnar_out | 11 | 310 | 275 | 275 |
| mnar_out | 12 | 301 | 270 | 269 |
| mnar_out | 13 | 327 | 298 | 298 |
| mnar_out | 14 | 311 | 288 | 287 |
| mnar_out | 15 | 300 | 268 | 268 |
| mnar_out | 16 | 312 | 281 | 281 |
| mnar_out | 17 | 309 | 283 | 283 |
| mnar_out | 18 | 325 | 301 | 301 |
| mnar_out | 19 | 313 | 287 | 287 |
| mnar_out | 20 | 311 | 285 | 284 |
| mnar_out | 21 | 306 | 271 | 271 |
| mnar_out | 22 | 308 | 285 | 284 |
| mnar_out | 23 | 312 | 282 | 282 |
| mnar_out | 24 | 315 | 288 | 288 |
| mnar_out | 25 | 329 | 294 | 293 |
| mnar_out | 26 | 320 | 289 | 289 |
| mnar_out | 27 | 317 | 288 | 288 |
| mnar_out | 28 | 299 | 276 | 276 |
| mnar_out | 29 | 337 | 303 | 303 |
| mnar_out | 30 | 317 | 291 | 290 |

## Ranking metrics across completed replicates

| Panel | Mechanism | Score | Metric | Replicates | Mean | SD |
|---|---|---|---|---:|---:|---:|
| reversal_orientation | mcar | already_observed_footprint | pr_auc | 30 | 0.5941 | 0.0111 |
| reversal_orientation | mcar | already_observed_footprint | precision_at_k | 30 | 0.5624 | 0.0063 |
| reversal_orientation | mcar | already_observed_footprint | recall_at_k | 30 | 0.5624 | 0.0063 |
| reversal_orientation | mcar | already_observed_footprint | roc_auc | 30 | 0.6069 | 0.0101 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7967 | 0.0171 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7355 | 0.0196 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7355 | 0.0196 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7892 | 0.0181 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.6060 | 0.0095 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5871 | 0.0150 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5871 | 0.0150 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.6199 | 0.0094 |
| reversal_orientation | mcar | lifted_cn_total_mean | pr_auc | 30 | 0.6209 | 0.0110 |
| reversal_orientation | mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6001 | 0.0149 |
| reversal_orientation | mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6001 | 0.0149 |
| reversal_orientation | mcar | lifted_cn_total_mean | roc_auc | 30 | 0.6394 | 0.0106 |
| reversal_orientation | mcar | lifted_degree_product_mean | pr_auc | 30 | 0.8655 | 0.0122 |
| reversal_orientation | mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.7824 | 0.0157 |
| reversal_orientation | mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.7824 | 0.0157 |
| reversal_orientation | mcar | lifted_degree_product_mean | roc_auc | 30 | 0.8622 | 0.0119 |
| reversal_orientation | mcar | lifted_ii_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oi_mean | pr_auc | 30 | 0.7797 | 0.0170 |
| reversal_orientation | mcar | lifted_oi_mean | precision_at_k | 30 | 0.7334 | 0.0193 |
| reversal_orientation | mcar | lifted_oi_mean | recall_at_k | 30 | 0.7334 | 0.0193 |
| reversal_orientation | mcar | lifted_oi_mean | roc_auc | 30 | 0.7882 | 0.0178 |
| reversal_orientation | mcar | lifted_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.4661 | 0.0024 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4227 | 0.0088 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4227 | 0.0088 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.3731 | 0.0123 |
| reversal_orientation | mnar_out | already_observed_footprint | pr_auc | 30 | 0.5926 | 0.0152 |
| reversal_orientation | mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5625 | 0.0099 |
| reversal_orientation | mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5625 | 0.0099 |
| reversal_orientation | mnar_out | already_observed_footprint | roc_auc | 30 | 0.6066 | 0.0152 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7731 | 0.0183 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7279 | 0.0153 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7279 | 0.0153 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7741 | 0.0165 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.5938 | 0.0104 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5745 | 0.0118 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5745 | 0.0118 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.6107 | 0.0097 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.6122 | 0.0114 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.5916 | 0.0141 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.5916 | 0.0141 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.6337 | 0.0118 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.8458 | 0.0150 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.7553 | 0.0172 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.7553 | 0.0172 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.8391 | 0.0141 |
| reversal_orientation | mnar_out | lifted_ii_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oi_mean | pr_auc | 30 | 0.7583 | 0.0177 |
| reversal_orientation | mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.7235 | 0.0138 |
| reversal_orientation | mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.7235 | 0.0138 |
| reversal_orientation | mnar_out | lifted_oi_mean | roc_auc | 30 | 0.7730 | 0.0167 |
| reversal_orientation | mnar_out | lifted_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.4621 | 0.0027 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4160 | 0.0094 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4160 | 0.0094 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.3655 | 0.0134 |
| role_exchange | mcar | already_observed_footprint | pr_auc | 30 | 0.5873 | 0.0111 |
| role_exchange | mcar | already_observed_footprint | precision_at_k | 30 | 0.5600 | 0.0064 |
| role_exchange | mcar | already_observed_footprint | recall_at_k | 30 | 0.5600 | 0.0064 |
| role_exchange | mcar | already_observed_footprint | roc_auc | 30 | 0.6023 | 0.0103 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5245 | 0.0060 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5262 | 0.0068 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5262 | 0.0068 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5330 | 0.0075 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7840 | 0.0200 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7249 | 0.0191 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7249 | 0.0191 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7802 | 0.0191 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.4794 | 0.0043 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.4712 | 0.0100 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.4712 | 0.0100 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.4642 | 0.0063 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.6094 | 0.0133 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5920 | 0.0158 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5920 | 0.0158 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.6273 | 0.0112 |
| role_exchange | mcar | lifted_cn_total_mean | pr_auc | 30 | 0.6181 | 0.0138 |
| role_exchange | mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6021 | 0.0148 |
| role_exchange | mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6021 | 0.0148 |
| role_exchange | mcar | lifted_cn_total_mean | roc_auc | 30 | 0.6414 | 0.0123 |
| role_exchange | mcar | lifted_degree_product_mean | pr_auc | 30 | 0.8491 | 0.0146 |
| role_exchange | mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.7717 | 0.0152 |
| role_exchange | mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.7717 | 0.0152 |
| role_exchange | mcar | lifted_degree_product_mean | roc_auc | 30 | 0.8508 | 0.0135 |
| role_exchange | mcar | lifted_ii_mean | pr_auc | 30 | 0.5225 | 0.0053 |
| role_exchange | mcar | lifted_ii_mean | precision_at_k | 30 | 0.5263 | 0.0056 |
| role_exchange | mcar | lifted_ii_mean | recall_at_k | 30 | 0.5263 | 0.0056 |
| role_exchange | mcar | lifted_ii_mean | roc_auc | 30 | 0.5331 | 0.0072 |
| role_exchange | mcar | lifted_oi_mean | pr_auc | 30 | 0.7681 | 0.0193 |
| role_exchange | mcar | lifted_oi_mean | precision_at_k | 30 | 0.7232 | 0.0182 |
| role_exchange | mcar | lifted_oi_mean | recall_at_k | 30 | 0.7232 | 0.0182 |
| role_exchange | mcar | lifted_oi_mean | roc_auc | 30 | 0.7790 | 0.0188 |
| role_exchange | mcar | lifted_oo_mean | pr_auc | 30 | 0.4815 | 0.0038 |
| role_exchange | mcar | lifted_oo_mean | precision_at_k | 30 | 0.4696 | 0.0091 |
| role_exchange | mcar | lifted_oo_mean | recall_at_k | 30 | 0.4696 | 0.0091 |
| role_exchange | mcar | lifted_oo_mean | roc_auc | 30 | 0.4624 | 0.0066 |
| role_exchange | mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.4688 | 0.0024 |
| role_exchange | mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4288 | 0.0081 |
| role_exchange | mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4288 | 0.0081 |
| role_exchange | mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.3852 | 0.0121 |
| role_exchange | mnar_out | already_observed_footprint | pr_auc | 30 | 0.5870 | 0.0150 |
| role_exchange | mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5605 | 0.0099 |
| role_exchange | mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5605 | 0.0099 |
| role_exchange | mnar_out | already_observed_footprint | roc_auc | 30 | 0.6027 | 0.0151 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5310 | 0.0063 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5277 | 0.0077 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5277 | 0.0077 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5367 | 0.0062 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7612 | 0.0186 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7177 | 0.0130 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7177 | 0.0130 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7641 | 0.0162 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.4836 | 0.0052 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.4775 | 0.0077 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.4775 | 0.0077 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.4672 | 0.0082 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.6104 | 0.0133 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5909 | 0.0136 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5909 | 0.0136 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.6277 | 0.0109 |
| role_exchange | mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.6204 | 0.0138 |
| role_exchange | mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.6029 | 0.0149 |
| role_exchange | mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.6029 | 0.0149 |
| role_exchange | mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.6441 | 0.0127 |
| role_exchange | mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.8297 | 0.0165 |
| role_exchange | mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.7452 | 0.0155 |
| role_exchange | mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.7452 | 0.0155 |
| role_exchange | mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.8278 | 0.0136 |
| role_exchange | mnar_out | lifted_ii_mean | pr_auc | 30 | 0.5284 | 0.0057 |
| role_exchange | mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.5294 | 0.0064 |
| role_exchange | mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.5294 | 0.0064 |
| role_exchange | mnar_out | lifted_ii_mean | roc_auc | 30 | 0.5372 | 0.0062 |
| role_exchange | mnar_out | lifted_oi_mean | pr_auc | 30 | 0.7467 | 0.0169 |
| role_exchange | mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.7119 | 0.0125 |
| role_exchange | mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.7119 | 0.0125 |
| role_exchange | mnar_out | lifted_oi_mean | roc_auc | 30 | 0.7626 | 0.0163 |
| role_exchange | mnar_out | lifted_oo_mean | pr_auc | 30 | 0.4837 | 0.0044 |
| role_exchange | mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.4755 | 0.0066 |
| role_exchange | mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.4755 | 0.0066 |
| role_exchange | mnar_out | lifted_oo_mean | roc_auc | 30 | 0.4658 | 0.0083 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.4661 | 0.0026 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4279 | 0.0110 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4279 | 0.0110 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.3856 | 0.0160 |

The `already_observed_footprint` column is a diagnostic baseline, not a prediction model. A valid hard negative must not be any known native event type, so an unavailable reversal or role exchange is recorded as a coverage limitation rather than relabelled.
