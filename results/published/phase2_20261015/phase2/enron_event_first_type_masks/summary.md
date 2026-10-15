# Event-first native-event-type mask summary

- Dataset: `enron_20150507`
- Unit sampled: a distinct ordered tail/head native event type; all duplicate message records of a selected type are withheld together.
- MCAR is exact fixed-count type sampling. MNAR-out is the planned oracle independent inclusion mechanism, so its realised type rate can differ from the nominal rate.
- An already-observed footprint is not leakage: it means at least one observed event of a different type induces every dyad of the held-out event type.

| Mechanism | Replicate | Type rate | Record rate | Arc-removal rate | Held-out types with surviving complete footprint | Active nodes losing out / in arcs |
|---|---:|---:|---:|---:|---:|---:|
| mcar | 1 | 0.2990 | 0.3271 | 0.2341 | 61/215 | 71/73 |
| mcar | 2 | 0.2990 | 0.2729 | 0.2277 | 67/215 | 75/72 |
| mcar | 3 | 0.2990 | 0.2724 | 0.2389 | 64/215 | 69/80 |
| mnar_out | 1 | 0.3213 | 0.5232 | 0.2420 | 39/231 | 41/77 |
| mnar_out | 2 | 0.2921 | 0.5119 | 0.2150 | 48/210 | 45/69 |
| mnar_out | 3 | 0.2893 | 0.4613 | 0.2261 | 29/208 | 42/74 |

`removal_strata.csv` in each split reports removal by tail/head arity and role degree decile. The degree deciles use deterministic equal-count actor ranks on the full cap-eligible native-event projection.
