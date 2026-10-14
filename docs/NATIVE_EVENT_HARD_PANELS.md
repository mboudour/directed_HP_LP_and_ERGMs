# Directed hard-negative panels for native-event recovery

The random, arity-matched panel answers whether a score distinguishes held-out native
event types from ordinary non-event groups. This separate benchmark asks whether the
same score preserves **directed role information** when the negative is structurally
close to the positive.

## Frozen-split input and universal safeguards

The driver reads only the observed event types, held-out event types, and observed
projection of each event-first split. A transformed candidate is valid only when it:

1. lies in that split's weak two-hop candidate universe;
2. has nonempty, disjoint tail and head roles;
3. is absent from **both** observed and held-out native-event types; and
4. is unique within its own hard panel.

A positive without a valid transformed non-event counterpart is reported as unavailable
for that panel. It is never assigned a random substitute. This preserves the intended
hard-negative interpretation.

## Panels

| Panel | Positive/negative pair | What it probes |
|---|---|---|
| `reversal_orientation` | `(T, H)` versus `(H, T)` | Whether a score knows the distinction between sender and recipient roles. Role arities naturally swap. |
| `role_exchange` | `(T, H)` versus a candidate with one tail actor and one head actor exchanged | Whether role placement matters conditional on exactly the same tail/head arities and actor set. |

Both panels reuse the same lifted dyadic scores and ranking-only metrics as the random
panel. A hard-panel score is not a calibrated probability, so the output includes
ROC-AUC, PR-AUC, precision@k, and recall@k—not log loss or fixed-threshold metrics.

## Enron command

```zsh
make phase2-enron-native-hard-panels
```

The target refreshes the deterministic event-first masks and writes ignored local
outputs under:

```text
results/phase2/enron_event_first_native_hard_panels/
```

Inspect `split_summary.csv` before interpreting the metrics: reversal and role-exchange
coverage are empirical properties of the observed split and of the requirement that a
hard negative be a true non-event type. This task does not yet cover degree-matched,
near-complete-footprint, or non-maximal-concept negatives; each has a distinct target
and will be implemented and reported separately.
