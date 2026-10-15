# Event-first native-event-type mask summary

- Dataset: `mathoverflow_stackexchange_2024`
- Unit sampled: a distinct ordered tail/head native event type; all duplicate message records of a selected type are withheld together.
- MCAR is exact fixed-count type sampling. MNAR-out and MNAR-in are planned oracle independent inclusion mechanisms, so their realised type rates can differ from nominal.
- An already-observed footprint is not leakage: it means at least one observed event of a different type induces every dyad of the held-out event type.

| Mechanism | Replicate | Type rate | Record rate | Arc-removal rate | Held-out types with surviving complete footprint | Active nodes losing out / in arcs |
|---|---:|---:|---:|---:|---:|---:|
| mcar | 1 | 0.2997 | 0.3088 | 0.2525 | 75/321 | 88/72 |
| mcar | 2 | 0.2997 | 0.3222 | 0.2495 | 72/321 | 90/63 |
| mcar | 3 | 0.2997 | 0.2821 | 0.2505 | 71/321 | 87/71 |
| mcar | 4 | 0.2997 | 0.2760 | 0.2377 | 85/321 | 85/68 |
| mcar | 5 | 0.2997 | 0.2621 | 0.2485 | 73/321 | 91/73 |
| mcar | 6 | 0.2997 | 0.2492 | 0.2692 | 59/321 | 89/72 |
| mcar | 7 | 0.2997 | 0.3078 | 0.2515 | 75/321 | 84/65 |
| mcar | 8 | 0.2997 | 0.3309 | 0.2406 | 83/321 | 90/68 |
| mcar | 9 | 0.2997 | 0.3176 | 0.2515 | 75/321 | 89/76 |
| mcar | 10 | 0.2997 | 0.2852 | 0.2426 | 80/321 | 85/72 |
| mcar | 11 | 0.2997 | 0.3073 | 0.2446 | 82/321 | 88/73 |
| mcar | 12 | 0.2997 | 0.3155 | 0.2475 | 71/321 | 84/69 |
| mcar | 13 | 0.2997 | 0.2816 | 0.2515 | 65/321 | 86/69 |
| mcar | 14 | 0.2997 | 0.3474 | 0.2574 | 77/321 | 88/72 |
| mcar | 15 | 0.2997 | 0.3094 | 0.2465 | 77/321 | 90/71 |
| mcar | 16 | 0.2997 | 0.3114 | 0.2564 | 71/321 | 88/71 |
| mcar | 17 | 0.2997 | 0.3099 | 0.2416 | 79/321 | 87/76 |
| mcar | 18 | 0.2997 | 0.3171 | 0.2495 | 77/321 | 85/74 |
| mcar | 19 | 0.2997 | 0.3489 | 0.2515 | 78/321 | 88/71 |
| mcar | 20 | 0.2997 | 0.2842 | 0.2505 | 74/321 | 87/73 |
| mcar | 21 | 0.2997 | 0.2955 | 0.2456 | 78/321 | 88/73 |
| mcar | 22 | 0.2997 | 0.2636 | 0.2594 | 70/321 | 85/73 |
| mcar | 23 | 0.2997 | 0.2672 | 0.2574 | 72/321 | 86/74 |
| mcar | 24 | 0.2997 | 0.3165 | 0.2515 | 72/321 | 90/68 |
| mcar | 25 | 0.2997 | 0.3109 | 0.2416 | 82/321 | 90/69 |
| mcar | 26 | 0.2997 | 0.3114 | 0.2436 | 80/321 | 86/71 |
| mcar | 27 | 0.2997 | 0.2965 | 0.2515 | 78/321 | 91/74 |
| mcar | 28 | 0.2997 | 0.3196 | 0.2406 | 79/321 | 86/72 |
| mcar | 29 | 0.2997 | 0.2739 | 0.2505 | 68/321 | 89/71 |
| mcar | 30 | 0.2997 | 0.3073 | 0.2485 | 74/321 | 91/72 |
| mnar_out | 1 | 0.3081 | 0.4003 | 0.2406 | 78/330 | 71/69 |
| mnar_out | 2 | 0.2932 | 0.3664 | 0.2209 | 72/314 | 69/68 |
| mnar_out | 3 | 0.2894 | 0.3823 | 0.2170 | 88/310 | 66/69 |
| mnar_out | 4 | 0.2969 | 0.3525 | 0.2485 | 73/318 | 79/71 |
| mnar_out | 5 | 0.3128 | 0.4034 | 0.2475 | 82/335 | 76/70 |
| mnar_out | 6 | 0.3072 | 0.4044 | 0.2337 | 84/329 | 73/69 |
| mnar_out | 7 | 0.2782 | 0.3669 | 0.2209 | 52/298 | 69/71 |
| mnar_out | 8 | 0.2988 | 0.3690 | 0.2377 | 67/320 | 63/72 |
| mnar_out | 9 | 0.2960 | 0.3905 | 0.2278 | 84/317 | 64/68 |
| mnar_out | 10 | 0.2829 | 0.3628 | 0.2249 | 58/303 | 69/74 |
| mnar_out | 11 | 0.2997 | 0.3988 | 0.2308 | 76/321 | 78/72 |
| mnar_out | 12 | 0.2848 | 0.3592 | 0.2071 | 88/305 | 58/65 |
| mnar_out | 13 | 0.3175 | 0.3977 | 0.2584 | 75/340 | 77/72 |
| mnar_out | 14 | 0.2997 | 0.3782 | 0.2406 | 73/321 | 71/69 |
| mnar_out | 15 | 0.2838 | 0.3582 | 0.2071 | 92/304 | 71/66 |
| mnar_out | 16 | 0.2997 | 0.3947 | 0.2387 | 71/321 | 77/73 |
| mnar_out | 17 | 0.2904 | 0.3834 | 0.2170 | 84/311 | 72/70 |
| mnar_out | 18 | 0.3109 | 0.3844 | 0.2416 | 79/333 | 74/77 |
| mnar_out | 19 | 0.3025 | 0.3895 | 0.2406 | 76/324 | 75/71 |
| mnar_out | 20 | 0.2988 | 0.3859 | 0.2189 | 84/320 | 73/71 |
| mnar_out | 21 | 0.2932 | 0.3551 | 0.2170 | 88/314 | 70/68 |
| mnar_out | 22 | 0.2969 | 0.3916 | 0.2387 | 71/318 | 68/70 |
| mnar_out | 23 | 0.3007 | 0.3947 | 0.2249 | 85/322 | 68/67 |
| mnar_out | 24 | 0.3025 | 0.4075 | 0.2436 | 88/324 | 71/70 |
| mnar_out | 25 | 0.3100 | 0.4018 | 0.2298 | 84/332 | 65/70 |
| mnar_out | 26 | 0.3025 | 0.4003 | 0.2249 | 87/324 | 69/69 |
| mnar_out | 27 | 0.3128 | 0.4142 | 0.2465 | 76/335 | 71/77 |
| mnar_out | 28 | 0.2848 | 0.3376 | 0.2249 | 79/305 | 74/73 |
| mnar_out | 29 | 0.3305 | 0.4162 | 0.2761 | 65/354 | 75/73 |
| mnar_out | 30 | 0.3025 | 0.3844 | 0.2416 | 69/324 | 73/74 |

`removal_strata.csv` in each split reports removal by tail/head arity and role degree decile. The degree deciles use deterministic equal-count actor ranks on the full cap-eligible native-event projection.
