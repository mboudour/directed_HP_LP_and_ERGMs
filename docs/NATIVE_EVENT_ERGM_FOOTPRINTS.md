# ERGM conditional footprint scores for native-event panels

This is the first ERGM comparison on the primary Enron **event-first native-event
type** evaluation. Its scope is deliberately narrower than a joint hyperlink model.
It estimates whether a fitted ERGM assigns high conditional support to a candidate's
**directed graph footprint**, not whether the recorded email group event occurred.

## Leakage-safe contract

For every frozen MCAR and MNAR-out event-first split:

1. `train_edges.csv` is the dyadic projection of **observed event types only**;
2. random, reversal/orientation, and role-exchange candidate panels are copied from
   their already frozen split-specific outputs;
3. all candidate footprints are expanded to their unique directed dyads;
4. each ERGM (`M0`, `M1`, `M3`, `M4c`) is re-estimated by MPLE on that split's
   training projection; and
5. exact conditional tie probabilities are obtained through Statnet's
   `predict(..., conditional = TRUE, type = "response")` call.

No full-network ERGM coefficients, raw emails, event records, or held-out graph are
used during the fit or scoring stage.

## Footprint scores

For a candidate footprint \(T \times H\) with conditional dyad probabilities
\(p_{th}\), the R driver reports:

| Score | Definition | Interpretation |
|---|---|---|
| `L1` | \(\operatorname{mean}_{t,h} p_{th}\) | Arithmetic conditional support across footprint arcs. |
| `L1g` | \(\exp[\operatorname{mean}_{t,h}\log p_{th}]\) | Size-normalized geometric support. |
| `L2` | \(\prod_{t,h}p_{th}\) | Single-dyad conditional-pseudolikelihood product used for the ranking pilot. |

The ranking evaluation uses `log_L2`, which is a strictly monotonic, numerically stable
representation of `L2`. More precisely, this initial `L2` is a product of **single-dyad
conditional-pseudolikelihood scores**, each conditioned on the split-specific training
network. It is a useful factorized ranking pilot, but it is **not** the matched-marginal
`L2` in the plan's dependence increment and is not the plan's joint simulation score
\(L3\)-F. The latter uses one candidate-specific observation constraint, conditional
simulation, and the same-draw marginal product; see
[`JOINT_FOOTPRINT_SIMULATION.md`](JOINT_FOOTPRINT_SIMULATION.md).

Although `L1`, `L1g`, and `L2` use ERGM conditional probabilities, none is a probability
that a recorded native email event occurred. Exact matching between a graph footprint and
an event type was already shown to fail in the Enron fidelity audit; this boundary is
therefore central to the interpretation.

## Metrics

The labels are native event types while the scores concern graph footprints. The driver
therefore reports only ranking metrics:

- ROC-AUC;
- PR-AUC;
- precision@k; and
- recall@k.

It does **not** report accuracy, F1, MCC, or log loss. Those would require an explicitly
trained event-type calibration model and an event-prevalence target, neither of which is
introduced here.

## Enron command

```zsh
make phase2-enron-native-ergm-footprints
```

The prerequisite target rebuilds all frozen source masks and panels deterministically,
then writes ERGM inputs under:

```text
results/phase2/enron_native_event_ergm_inputs/
```

The ERGM output is local and ignored by Git:

```text
results/models/enron_native_event_ergm_footprints/
```

Before comparing values, inspect `model_status.csv` and `split_status.csv`. A fit or
conditional-prediction failure remains visible by model and split; it is never replaced
with a full-network fit or a simpler model. The next, distinct step after this factorized
comparison is conditional ERGM simulation for \(L3\)-F, followed by the maximality
requirement \(L3\)-C for the derived concept target.
