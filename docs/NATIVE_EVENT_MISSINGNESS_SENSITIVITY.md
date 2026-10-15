# Supplementary native-event missingness sensitivity

## Scope

This protocol supplements—but does not replace—the predeclared **30% MCAR and
MNAR-out** primary native-event results. It assesses whether the uncalibrated
native-event heuristic and directed hard-panel rankings are materially altered
at event-type withholding rates of **10%, 20%, and 50%**, and under an added
oracle **MNAR-in** mechanism.

No new static or temporal ERGM fit is selected from this grid. ERGM results
retain the primary frozen 30% protocol. This preserves the paper's stated
primary analysis and prevents post-hoc selection of a favorable rate or
mechanism.

## Mechanisms

- **MCAR:** exact fixed-count sampling of native event types.
- **MNAR-out:** independent oracle selection probabilities proportional to
  full-data mean tail-role activity.
- **MNAR-in:** independent oracle selection probabilities proportional to
  full-data mean head-role activity.

For both MNAR variants, realised type, record, and dyadic removal rates are
reported. They need not equal the requested rate.

## Outputs

For each rate and mechanism, the runner creates fresh event-first masks,
repeats native-event heuristic ranking and the reversal/role-exchange hard
panels, then publishes only aggregate masking and metric tables. Candidate
rows, event records, role labels, and actor-level activity maps remain outside
the publication bundle.

## Reproduction

```bash
make phase2-enron-native-sensitivity
make phase2-mathoverflow-native-sensitivity
```
