# Event-first native-event-type masking

This implements **Regime A** of the agreed design for data with recorded group events.
For Enron, the primary target is a distinct ordered tail/head **event type** in the
fixed core-100 actor universe. A repeated record of the same tail/head type is not a
new prediction target.

## Why types, rather than individual message records

If only one copy of a recurring email type were hidden, an identical tail/head event
could remain visible in the observed data. Treating the removed copy as an unknown
native event would therefore be a direct target leak. This implementation groups
identical tail/head records first and hides **every copy of a selected type**.

The observed static graph is then constructed from the observed event types only:

```text
H_obs = H_native_types \ M_types
D_obs = projection(H_obs)
```

Some arcs of a held-out event type can still survive in `D_obs` because other observed
*event types* use them. That is a substantive feature of event-first masking, not
leakage. The split records the fraction of held-out types whose entire footprints remain
observed as the required “already-observed footprint” baseline.

## Missingness mechanisms

- **MCAR:** fixed-count, uniform sampling without replacement from cap-eligible native
  event types. The realized type rate is the planned floor-rate rate.
- **MNAR-out:** the planned oracle role-biased simulation. Sender activity is computed
  on the full cap-eligible data as the sender's total recipient incidence, and each
  type has independent inclusion probability `min(1, lambda * sender_activity)`. The
  driver solves `lambda` so the *expected* mean inclusion probability is the requested
  rate. The realized rate is reported and can differ from the nominal rate.

Both mechanisms make their dependence on full data explicit. MNAR-out is an oracle
missingness stress test, not a claimed missingness mechanism for Enron.

## Enron pilot command

```zsh
make phase2-enron-event-masks
```

The fixed target uses tail/head caps of 3, a 30% nominal rate, three MCAR replicates,
and three MNAR-out replicates. It prints the compact realized-rate table and writes an
ignored local result bundle in:

```text
results/phase2/enron_event_first_type_masks/
```

Each split has:

| File | Purpose |
|---|---|
| `observed_event_types.csv` | Type-level native-event training input, preserving record multiplicity as `occurrence_count`. |
| `heldout_event_types.csv` | Positive native-event targets with their footprint-survival diagnostic. |
| `observed_arcs.csv` | Exact dyadic projection of the observed event types. |
| `removed_arcs.csv` | Distinct arcs removed from the cap-restricted full projection. |
| `removal_strata.csv` | Realized masking by tail/head arity and degree decile. |
| `manifest.json` | Split-level rate accounting, seeds, and source contract. |

No candidate negatives, native-event scores, calibrated probability metrics, or
role-assignment scores are produced at this step. Those must be constructed from each
specific observed split, never from the complete native-event data.
