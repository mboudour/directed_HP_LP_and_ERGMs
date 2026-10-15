# Event-first native-event-type mask summary

- Dataset: `mathoverflow_stackexchange_2024`
- Unit sampled: a distinct ordered tail/head native event type; all duplicate message records of a selected type are withheld together.
- MCAR is exact fixed-count type sampling. MNAR-out is the planned oracle independent inclusion mechanism, so its realised type rate can differ from the nominal rate.
- An already-observed footprint is not leakage: it means at least one observed event of a different type induces every dyad of the held-out event type.

| Mechanism | Replicate | Type rate | Record rate | Arc-removal rate | Held-out types with surviving complete footprint | Active nodes losing out / in arcs |
|---|---:|---:|---:|---:|---:|---:|
| mcar | 1 | 0.2997 | 0.3088 | 0.2525 | 75/321 | 88/72 |
| mcar | 2 | 0.2997 | 0.3222 | 0.2495 | 72/321 | 90/63 |
| mcar | 3 | 0.2997 | 0.2821 | 0.2505 | 71/321 | 87/71 |
| mnar_out | 1 | 0.3081 | 0.4003 | 0.2406 | 78/330 | 71/69 |
| mnar_out | 2 | 0.2932 | 0.3664 | 0.2209 | 72/314 | 69/68 |
| mnar_out | 3 | 0.2894 | 0.3823 | 0.2170 | 88/310 | 66/69 |

`removal_strata.csv` in each split reports removal by tail/head arity and role degree decile. The degree deciles use deterministic equal-count actor ranks on the full cap-eligible native-event projection.
