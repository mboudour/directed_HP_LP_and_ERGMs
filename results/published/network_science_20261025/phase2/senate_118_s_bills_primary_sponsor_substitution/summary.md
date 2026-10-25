# Senate sponsor-substitution hard-negative benchmark

- Dataset: `senate_118_s_bills`
- Each pair retains one sponsor and the same bill participants by exchanging the sponsor with one original co-sponsor.
- Reversal/orientation is absent because it would turn a 1-to-h bill into h-to-1 roles.

## Coverage

| Mechanism | Replicate | Eligible held-out types | Sponsor-substitution pairs |
|---|---:|---:|---:|
| mcar | 1 | 962 | 812 |
| mcar | 2 | 961 | 832 |
| mcar | 3 | 961 | 813 |
| mcar | 4 | 962 | 828 |
| mcar | 5 | 962 | 820 |
| mcar | 6 | 962 | 824 |
| mcar | 7 | 961 | 819 |
| mcar | 8 | 960 | 830 |
| mcar | 9 | 961 | 815 |
| mcar | 10 | 961 | 827 |
| mcar | 11 | 962 | 820 |
| mcar | 12 | 962 | 829 |
| mcar | 13 | 962 | 839 |
| mcar | 14 | 962 | 816 |
| mcar | 15 | 962 | 826 |
| mcar | 16 | 961 | 816 |
| mcar | 17 | 962 | 829 |
| mcar | 18 | 962 | 806 |
| mcar | 19 | 962 | 822 |
| mcar | 20 | 962 | 829 |
| mcar | 21 | 961 | 812 |
| mcar | 22 | 962 | 835 |
| mcar | 23 | 960 | 821 |
| mcar | 24 | 962 | 827 |
| mcar | 25 | 962 | 825 |
| mcar | 26 | 962 | 815 |
| mcar | 27 | 960 | 821 |
| mcar | 28 | 962 | 825 |
| mcar | 29 | 959 | 799 |
| mcar | 30 | 962 | 826 |
| mnar_out | 1 | 946 | 828 |
| mnar_out | 2 | 972 | 850 |
| mnar_out | 3 | 962 | 846 |
| mnar_out | 4 | 964 | 832 |
| mnar_out | 5 | 925 | 808 |
| mnar_out | 6 | 1024 | 901 |
| mnar_out | 7 | 952 | 832 |
| mnar_out | 8 | 975 | 852 |
| mnar_out | 9 | 972 | 846 |
| mnar_out | 10 | 993 | 861 |
| mnar_out | 11 | 935 | 810 |
| mnar_out | 12 | 982 | 856 |
| mnar_out | 13 | 982 | 850 |
| mnar_out | 14 | 924 | 787 |
| mnar_out | 15 | 955 | 818 |
| mnar_out | 16 | 984 | 872 |
| mnar_out | 17 | 967 | 842 |
| mnar_out | 18 | 992 | 874 |
| mnar_out | 19 | 964 | 825 |
| mnar_out | 20 | 985 | 843 |
| mnar_out | 21 | 989 | 842 |
| mnar_out | 22 | 967 | 825 |
| mnar_out | 23 | 947 | 824 |
| mnar_out | 24 | 962 | 821 |
| mnar_out | 25 | 952 | 812 |
| mnar_out | 26 | 959 | 823 |
| mnar_out | 27 | 958 | 824 |
| mnar_out | 28 | 930 | 810 |
| mnar_out | 29 | 938 | 812 |
| mnar_out | 30 | 1000 | 875 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 30 | 0.5219 | 0.0058 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.5311 | 0.0078 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.5311 | 0.0078 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.5393 | 0.0096 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.4930 | 0.0066 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.4932 | 0.0070 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.4932 | 0.0070 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.4896 | 0.0073 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.5782 | 0.0112 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.5622 | 0.0096 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.5622 | 0.0096 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.5875 | 0.0104 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5278 | 0.0057 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5248 | 0.0062 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5248 | 0.0062 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5346 | 0.0062 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.5358 | 0.0069 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5309 | 0.0076 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5309 | 0.0076 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.5418 | 0.0072 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.5375 | 0.0071 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.5328 | 0.0073 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.5328 | 0.0073 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.5445 | 0.0073 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.5799 | 0.0123 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.5628 | 0.0099 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.5628 | 0.0099 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.5896 | 0.0112 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.4928 | 0.0064 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.4930 | 0.0070 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.4930 | 0.0070 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.4889 | 0.0072 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.5769 | 0.0109 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.5621 | 0.0099 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.5621 | 0.0099 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.5874 | 0.0104 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.5271 | 0.0057 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.5253 | 0.0067 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.5253 | 0.0067 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.5345 | 0.0062 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.4922 | 0.0061 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4906 | 0.0089 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4906 | 0.0089 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.4872 | 0.0096 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.5201 | 0.0060 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5297 | 0.0084 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5297 | 0.0084 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.5365 | 0.0101 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5038 | 0.0050 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5130 | 0.0069 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5130 | 0.0069 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5140 | 0.0063 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.5630 | 0.0133 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.5637 | 0.0127 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.5637 | 0.0127 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.5900 | 0.0138 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5263 | 0.0070 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5344 | 0.0109 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5344 | 0.0109 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5473 | 0.0098 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.5297 | 0.0073 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5418 | 0.0101 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5418 | 0.0101 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.5548 | 0.0085 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.5310 | 0.0076 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.5422 | 0.0108 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.5422 | 0.0108 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.5567 | 0.0088 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.5668 | 0.0160 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.5568 | 0.0168 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.5568 | 0.0168 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.5903 | 0.0178 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.5035 | 0.0051 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.5118 | 0.0074 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.5118 | 0.0074 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.5131 | 0.0064 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.5621 | 0.0132 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.5639 | 0.0127 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.5639 | 0.0127 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.5899 | 0.0139 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.5258 | 0.0073 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.5344 | 0.0111 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.5344 | 0.0111 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.5471 | 0.0100 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.5038 | 0.0060 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.5083 | 0.0088 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.5083 | 0.0088 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.5065 | 0.0094 |
