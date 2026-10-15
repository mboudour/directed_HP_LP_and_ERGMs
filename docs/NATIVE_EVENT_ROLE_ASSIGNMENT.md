# Native-event role assignment

## Question

For every held-out native event type, the node set is supplied but its tail/head
assignment is hidden. The evaluator ranks **every partition of that node set**
with the true tail and head arities. In a one-sender email, this is precisely
the task of choosing the sender from the event participants.

## Leakage and scoring

The procedure uses only the observed directed projection of each frozen
event-first split. It does not use observed or held-out native-event labels to
remove alternative partitions: if an alternative partition is itself a known
native-event type, it remains an admissible role assignment for the known
participant set.

The score family is deliberately identical to the native-event heuristic
benchmark: directed common-neighbour counts, directed Adamic--Adar variants,
reverse-arc fraction, degree product, and the already-observed-footprint
diagnostic. All are uncalibrated ranking scores.

## Metrics

- **Top-1 accuracy:** probability that the true partition is first under uniform
  resolution of score ties.
- **MRR:** expected reciprocal rank under the same tie policy.
- **Correct-score-exceeds-reversal:** reported only when a reversal is a
  compatible same-arity partition, which is principally the `1 -> 1` case.

Results are stratified by tail and head arity. There is no case-control panel,
so these are role-assignment metrics rather than prevalence-dependent
classification metrics.

## Reproduction

```bash
make phase2-enron-role-assignment
make phase2-mathoverflow-role-assignment
```

Aggregate-only summaries are copied to the private publication bundle by
`make phase2-publish-aggregate`.
