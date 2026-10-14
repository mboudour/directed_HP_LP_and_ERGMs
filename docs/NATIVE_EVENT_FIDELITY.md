# Native-event versus formal-concept fidelity audit

The paper keeps three target layers distinct: **recorded native events**, **derived formal
concepts**, and **directed footprints**. This audit provides the required empirical bridge
between the first two before native-event or concept-recovery experiments are interpreted.

For a prepared native-event table, a fixed node universe, and the corresponding static
directed relation, `scripts/29_audit_native_event_fidelity.py`:

1. filters native events to the fixed actor universe and removes invalid empty or
   role-overlapping records;
2. groups repeated message records into exact tail/head **event types**, retaining their
   record multiplicity separately;
3. applies the explicit tail/head caps to the native-event types and enumerates the
   formal-concept section with the same cap-first bounds;
4. measures exact tail/head equality, footprint overlap, bidirectional best
   role-sensitive Jaccard matches, concept aggregation ratios, strict contained-concept
   fragmentation, and best-match role distortion; and
5. writes only anonymized type/concept identifiers in its match tables, plus a reproducible
   input-hash manifest and an aggregate summary.

## Enron primary command

After the strict core-100 projection and cap-3 concept audit, run:

```zsh
make phase2-enron-native-fidelity
```

It creates the ignored local bundle:

```text
results/phase2/enron_native_event_fidelity_tail3_head3/
```

## Interpretation boundary

- An exact tail/head match is the strongest evidence that a derived concept agrees with a
  recorded event type; it is not required for footprint overlap.
- The event-to-concept and concept-to-event best role similarities use the plan's
  role-sensitive Jaccard index, assigning equal weight to tail and head membership.
- A concept's aggregation ratio counts the capped recorded native-event types and message
  occurrences that contribute at least one footprint arc. It describes many-to-one
  aggregation; it is **not** an inverse reconstruction.
- “Spurious closure” here means a formal concept without an exact recorded-event type,
  not a claim that the observed graph contains an error.
- The capped section is a deliberate computational representation. It does not establish
  equivalence between formal concepts and messages, and this first audit does not yet use
  degree-preserving rewiring to produce a chance-corrected fidelity comparison.
