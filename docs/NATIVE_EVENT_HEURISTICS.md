# Event-first native-event heuristic benchmark

This is the first predictive comparison on the primary Enron **recorded native-event
type** target. It consumes the frozen event-first masks rather than the complete
network, so every score uses only the observed graph of its own split.

## Candidate and label policy

For each held-out native tail/head event type:

1. the candidate is retained only when every pair of participants is at weak graph
distance at most two in the split's observed directed projection;
2. one random negative event type is sampled with exactly the same tail and head
arities;
3. negatives are required to be absent from **both** the observed and held-out native
event-type sets, so a known message type can never be labelled negative; and
4. the resulting panel is 1:1 case-control and is used for ranking only.

Positives outside the observed-split candidate universe are not silently reclassified or
replaced; their number and eligibility rate are recorded for every split.

## Scores

Each candidate score is the arithmetic mean across its footprint dyads of one of:

- reverse-arc indicator;
- source out-degree × target in-degree;
- directed OI/two-path, OO/shared-target, II/shared-source, and total common-neighbor
  counts;
- their corresponding directed Adamic–Adar scores.

The additional `already_observed_footprint` baseline is **not a predictive method**. It
is one when all arcs of a held-out event type are still present because other observed
event types induced them. Its purpose is to reveal what dyadic information survives
event-first masking.

These are uncalibrated ranking scores. The output therefore reports only **ROC-AUC,
PR-AUC, precision@k, and recall@k**. Accuracy, F1, MCC, and log loss require a threshold
or probability calibration map learned on training data; they are intentionally not
reported for raw local scores.

## Enron pilot command

```zsh
make phase2-enron-native-heuristics
```

The target deterministically refreshes the six event-first source masks and evaluates
all six splits. The local, ignored output bundle is:

```text
results/phase2/enron_event_first_native_heuristics/
```

It has a per-split `candidate_predictions.csv` and `metrics.csv`, together with
cross-replicate `split_summary.csv`, `metric_summary.csv`, `summary.md`, and a manifest.
This evaluates only the primary **random, arity-matched negative panel**. Degree-matched,
near-complete, role-corrupted, and reversal panels remain separate follow-on tasks; no
single easy-negative result will be treated as a complete native-event evaluation.
