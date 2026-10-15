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
| mcar | 4 | 206 | 88 | 83 |
| mcar | 5 | 200 | 89 | 85 |
| mcar | 6 | 196 | 84 | 79 |
| mcar | 7 | 211 | 94 | 88 |
| mcar | 8 | 206 | 87 | 79 |
| mcar | 9 | 201 | 83 | 78 |
| mcar | 10 | 201 | 84 | 81 |
| mcar | 11 | 196 | 87 | 81 |
| mcar | 12 | 196 | 73 | 68 |
| mcar | 13 | 195 | 75 | 69 |
| mcar | 14 | 187 | 77 | 75 |
| mcar | 15 | 208 | 97 | 89 |
| mcar | 16 | 205 | 102 | 95 |
| mcar | 17 | 202 | 94 | 90 |
| mcar | 18 | 204 | 82 | 76 |
| mcar | 19 | 196 | 78 | 74 |
| mcar | 20 | 198 | 84 | 76 |
| mcar | 21 | 206 | 92 | 82 |
| mcar | 22 | 201 | 77 | 73 |
| mcar | 23 | 205 | 83 | 77 |
| mcar | 24 | 204 | 92 | 88 |
| mcar | 25 | 200 | 84 | 77 |
| mcar | 26 | 207 | 83 | 77 |
| mcar | 27 | 201 | 80 | 76 |
| mcar | 28 | 206 | 83 | 77 |
| mcar | 29 | 199 | 86 | 79 |
| mcar | 30 | 200 | 82 | 79 |
| mnar_out | 1 | 224 | 95 | 81 |
| mnar_out | 2 | 194 | 90 | 82 |
| mnar_out | 3 | 203 | 96 | 89 |
| mnar_out | 4 | 213 | 94 | 85 |
| mnar_out | 5 | 202 | 86 | 77 |
| mnar_out | 6 | 207 | 95 | 83 |
| mnar_out | 7 | 199 | 85 | 75 |
| mnar_out | 8 | 202 | 95 | 84 |
| mnar_out | 9 | 211 | 93 | 84 |
| mnar_out | 10 | 197 | 79 | 72 |
| mnar_out | 11 | 191 | 92 | 84 |
| mnar_out | 12 | 207 | 89 | 77 |
| mnar_out | 13 | 197 | 97 | 88 |
| mnar_out | 14 | 202 | 92 | 82 |
| mnar_out | 15 | 199 | 94 | 87 |
| mnar_out | 16 | 206 | 96 | 87 |
| mnar_out | 17 | 186 | 83 | 75 |
| mnar_out | 18 | 215 | 98 | 84 |
| mnar_out | 19 | 214 | 94 | 84 |
| mnar_out | 20 | 213 | 97 | 84 |
| mnar_out | 21 | 193 | 93 | 84 |
| mnar_out | 22 | 200 | 83 | 75 |
| mnar_out | 23 | 201 | 97 | 85 |
| mnar_out | 24 | 210 | 97 | 85 |
| mnar_out | 25 | 210 | 96 | 88 |
| mnar_out | 26 | 197 | 93 | 84 |
| mnar_out | 27 | 200 | 87 | 78 |
| mnar_out | 28 | 197 | 87 | 80 |
| mnar_out | 29 | 218 | 91 | 79 |
| mnar_out | 30 | 213 | 89 | 81 |

## Ranking metrics across completed replicates

| Panel | Mechanism | Score | Metric | Replicates | Mean | SD |
|---|---|---|---|---:|---:|---:|
| reversal_orientation | mcar | already_observed_footprint | pr_auc | 30 | 0.5228 | 0.0176 |
| reversal_orientation | mcar | already_observed_footprint | precision_at_k | 30 | 0.5270 | 0.0208 |
| reversal_orientation | mcar | already_observed_footprint | recall_at_k | 30 | 0.5270 | 0.0208 |
| reversal_orientation | mcar | already_observed_footprint | roc_auc | 30 | 0.5380 | 0.0288 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.5336 | 0.0277 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.5098 | 0.0290 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.5098 | 0.0290 |
| reversal_orientation | mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.5227 | 0.0309 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.5177 | 0.0118 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5046 | 0.0146 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5046 | 0.0146 |
| reversal_orientation | mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.5076 | 0.0106 |
| reversal_orientation | mcar | lifted_cn_total_mean | pr_auc | 30 | 0.5187 | 0.0117 |
| reversal_orientation | mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.5031 | 0.0150 |
| reversal_orientation | mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.5031 | 0.0150 |
| reversal_orientation | mcar | lifted_cn_total_mean | roc_auc | 30 | 0.5107 | 0.0117 |
| reversal_orientation | mcar | lifted_degree_product_mean | pr_auc | 30 | 0.5731 | 0.0223 |
| reversal_orientation | mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.5432 | 0.0296 |
| reversal_orientation | mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.5432 | 0.0296 |
| reversal_orientation | mcar | lifted_degree_product_mean | roc_auc | 30 | 0.5624 | 0.0236 |
| reversal_orientation | mcar | lifted_ii_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oi_mean | pr_auc | 30 | 0.5290 | 0.0227 |
| reversal_orientation | mcar | lifted_oi_mean | precision_at_k | 30 | 0.5159 | 0.0265 |
| reversal_orientation | mcar | lifted_oi_mean | recall_at_k | 30 | 0.5159 | 0.0265 |
| reversal_orientation | mcar | lifted_oi_mean | roc_auc | 30 | 0.5258 | 0.0286 |
| reversal_orientation | mcar | lifted_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.4784 | 0.0144 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4756 | 0.0139 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4756 | 0.0139 |
| reversal_orientation | mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.4634 | 0.0212 |
| reversal_orientation | mnar_out | already_observed_footprint | pr_auc | 30 | 0.4776 | 0.0066 |
| reversal_orientation | mnar_out | already_observed_footprint | precision_at_k | 30 | 0.4576 | 0.0171 |
| reversal_orientation | mnar_out | already_observed_footprint | recall_at_k | 30 | 0.4576 | 0.0171 |
| reversal_orientation | mnar_out | already_observed_footprint | roc_auc | 30 | 0.4378 | 0.0256 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5000 | 0.0003 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.4470 | 0.0232 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.3926 | 0.0245 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.3926 | 0.0245 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.3628 | 0.0222 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.4792 | 0.0099 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.4462 | 0.0238 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.4462 | 0.0238 |
| reversal_orientation | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.4457 | 0.0120 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.4751 | 0.0117 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.4337 | 0.0259 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.4337 | 0.0259 |
| reversal_orientation | mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.4356 | 0.0143 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.4531 | 0.0246 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.4097 | 0.0221 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.4097 | 0.0221 |
| reversal_orientation | mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.3615 | 0.0228 |
| reversal_orientation | mnar_out | lifted_ii_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_ii_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oi_mean | pr_auc | 30 | 0.4489 | 0.0183 |
| reversal_orientation | mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.4071 | 0.0232 |
| reversal_orientation | mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.4071 | 0.0232 |
| reversal_orientation | mnar_out | lifted_oi_mean | roc_auc | 30 | 0.3681 | 0.0234 |
| reversal_orientation | mnar_out | lifted_oo_mean | pr_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_oo_mean | roc_auc | 30 | 0.5000 | 0.0000 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.5685 | 0.0233 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6010 | 0.0186 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6010 | 0.0186 |
| reversal_orientation | mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.6080 | 0.0231 |
| role_exchange | mcar | already_observed_footprint | pr_auc | 30 | 0.5362 | 0.0225 |
| role_exchange | mcar | already_observed_footprint | precision_at_k | 30 | 0.5375 | 0.0226 |
| role_exchange | mcar | already_observed_footprint | recall_at_k | 30 | 0.5375 | 0.0226 |
| role_exchange | mcar | already_observed_footprint | roc_auc | 30 | 0.5559 | 0.0328 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5074 | 0.0193 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.4911 | 0.0092 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.4911 | 0.0092 |
| role_exchange | mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.4911 | 0.0128 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.5322 | 0.0245 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.5250 | 0.0351 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.5250 | 0.0351 |
| role_exchange | mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.5333 | 0.0330 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5123 | 0.0131 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5132 | 0.0160 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5132 | 0.0160 |
| role_exchange | mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5106 | 0.0157 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.5197 | 0.0160 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5089 | 0.0226 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5089 | 0.0226 |
| role_exchange | mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.5115 | 0.0182 |
| role_exchange | mcar | lifted_cn_total_mean | pr_auc | 30 | 0.5205 | 0.0141 |
| role_exchange | mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.5089 | 0.0223 |
| role_exchange | mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.5089 | 0.0223 |
| role_exchange | mcar | lifted_cn_total_mean | roc_auc | 30 | 0.5146 | 0.0183 |
| role_exchange | mcar | lifted_degree_product_mean | pr_auc | 30 | 0.5827 | 0.0230 |
| role_exchange | mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.5648 | 0.0304 |
| role_exchange | mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.5648 | 0.0304 |
| role_exchange | mcar | lifted_degree_product_mean | roc_auc | 30 | 0.5842 | 0.0257 |
| role_exchange | mcar | lifted_ii_mean | pr_auc | 30 | 0.4997 | 0.0122 |
| role_exchange | mcar | lifted_ii_mean | precision_at_k | 30 | 0.4903 | 0.0110 |
| role_exchange | mcar | lifted_ii_mean | recall_at_k | 30 | 0.4903 | 0.0110 |
| role_exchange | mcar | lifted_ii_mean | roc_auc | 30 | 0.4904 | 0.0117 |
| role_exchange | mcar | lifted_oi_mean | pr_auc | 30 | 0.5295 | 0.0216 |
| role_exchange | mcar | lifted_oi_mean | precision_at_k | 30 | 0.5280 | 0.0314 |
| role_exchange | mcar | lifted_oi_mean | recall_at_k | 30 | 0.5280 | 0.0314 |
| role_exchange | mcar | lifted_oi_mean | roc_auc | 30 | 0.5352 | 0.0298 |
| role_exchange | mcar | lifted_oo_mean | pr_auc | 30 | 0.5103 | 0.0112 |
| role_exchange | mcar | lifted_oo_mean | precision_at_k | 30 | 0.5107 | 0.0161 |
| role_exchange | mcar | lifted_oo_mean | recall_at_k | 30 | 0.5107 | 0.0161 |
| role_exchange | mcar | lifted_oo_mean | roc_auc | 30 | 0.5098 | 0.0146 |
| role_exchange | mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.4781 | 0.0100 |
| role_exchange | mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4736 | 0.0143 |
| role_exchange | mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4736 | 0.0143 |
| role_exchange | mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.4617 | 0.0176 |
| role_exchange | mnar_out | already_observed_footprint | pr_auc | 30 | 0.4815 | 0.0073 |
| role_exchange | mnar_out | already_observed_footprint | precision_at_k | 30 | 0.4663 | 0.0181 |
| role_exchange | mnar_out | already_observed_footprint | recall_at_k | 30 | 0.4663 | 0.0181 |
| role_exchange | mnar_out | already_observed_footprint | roc_auc | 30 | 0.4489 | 0.0275 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5475 | 0.0168 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5225 | 0.0154 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5225 | 0.0154 |
| role_exchange | mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5362 | 0.0111 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.4579 | 0.0215 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.4012 | 0.0325 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.4012 | 0.0325 |
| role_exchange | mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.3815 | 0.0281 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.4947 | 0.0098 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.4621 | 0.0184 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.4621 | 0.0184 |
| role_exchange | mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.4523 | 0.0118 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.4890 | 0.0131 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.4501 | 0.0275 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.4501 | 0.0275 |
| role_exchange | mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.4556 | 0.0152 |
| role_exchange | mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.4824 | 0.0127 |
| role_exchange | mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.4336 | 0.0241 |
| role_exchange | mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.4336 | 0.0241 |
| role_exchange | mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.4419 | 0.0171 |
| role_exchange | mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.4797 | 0.0301 |
| role_exchange | mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.4286 | 0.0254 |
| role_exchange | mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.4286 | 0.0254 |
| role_exchange | mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.3962 | 0.0271 |
| role_exchange | mnar_out | lifted_ii_mean | pr_auc | 30 | 0.5375 | 0.0140 |
| role_exchange | mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.5190 | 0.0121 |
| role_exchange | mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.5190 | 0.0121 |
| role_exchange | mnar_out | lifted_ii_mean | roc_auc | 30 | 0.5338 | 0.0116 |
| role_exchange | mnar_out | lifted_oi_mean | pr_auc | 30 | 0.4594 | 0.0185 |
| role_exchange | mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.4087 | 0.0286 |
| role_exchange | mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.4087 | 0.0286 |
| role_exchange | mnar_out | lifted_oi_mean | roc_auc | 30 | 0.3855 | 0.0287 |
| role_exchange | mnar_out | lifted_oo_mean | pr_auc | 30 | 0.4902 | 0.0078 |
| role_exchange | mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.4581 | 0.0174 |
| role_exchange | mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.4581 | 0.0174 |
| role_exchange | mnar_out | lifted_oo_mean | roc_auc | 30 | 0.4497 | 0.0121 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.5515 | 0.0173 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.5261 | 0.0204 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.5261 | 0.0204 |
| role_exchange | mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.5523 | 0.0209 |

The `already_observed_footprint` column is a diagnostic baseline, not a prediction model. A valid hard negative must not be any known native event type, so an unavailable reversal or role exchange is recorded as a coverage limitation rather than relabelled.
