# Paired frozen-mask uncertainty analysis

## Purpose

For the primary native-event analyses, every method is evaluated on the same
frozen **30 MCAR** and **30 MNAR-out** masks per dataset. This module converts
replicate-level metrics into within-dataset contrasts without treating
candidates, dyads, or masks from different datasets as independent networks.

## Predeclared contrasts

- **Native heuristic scores:** each score is compared with
  `lifted_adamic_adar_total_mean`, the aggregate directed Adamic--Adar
  reference score.
- **Native ERGM footprint scores:** every model/score combination is compared
  with `M0::L1`, the edges-only factorized footprint reference.

The output covers all available mechanisms, target panels, and ranking metrics.
No comparison is selected after inspecting the results.

## Inference

For each comparison, the statistic is the mean of the score difference within
matched whole-mask replicates.

- **95% percentile bootstrap interval:** 10,000 resamples of the 30 paired
  masks.
- **Two-sided paired sign-flip test:** 20,000 Monte-Carlo sign assignments.

The results are **within-dataset**. They are not a cross-network meta-analysis;
distributions of the two datasets' effects must be shown separately.

## Reproduction

```bash
make phase2-enron-paired-uncertainty
make phase2-mathoverflow-paired-uncertainty
```
