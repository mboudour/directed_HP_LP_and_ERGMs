# Paper 1 manuscript plan-compliance audit

**Audited source:** `manuscript/snam/Paper1_SNAM.tex`

**Audit basis:** agreed paper skeleton, the final Phase 2 completion review, and the admitted aggregate-only Phase 2 result bundle.
**Purpose:** record how the canonical TeX draft retains the agreed scientific agenda while making the Phase 2 evidence boundary explicit. This is a manuscript-development audit, not a claim that every originally proposed analysis was computationally admissible.

## Compliance map

| Agreed-plan requirement | Canonical manuscript location | Implemented evidence boundary |
|---|---|---|
| Exact working title supplied by the author | Title and abstract | **Exponential Random Graph Models as a Statistical Benchmark for Directed Link and Hyperlink Prediction** |
| Directed graph/hypergraph objects and 2-section | Sections 2.1–2.2 | Defines ordered tail/head hyperarcs, the many-to-one projection, and a three-actor non-identifiability construction. |
| Predecessor–successor Galois connection and formal concepts | Section 2.2 | Defines the two derivation maps, concepts as maximal directed all-ones rectangles, `f(D)`, proof that `π(f(D)) = D`, the symmetric/reflexive clique relation, and a directed worked example. |
| Distinguish native interactions from derived structural targets | Sections 2–3 and 6.1 | Uses a target ladder: footprints, cap-first formal concepts, and native/reconstructed ordered event types. Exact event–concept equality is audited separately from footprint overlap. |
| Directed local scores and their ERGM relation | Sections 2.3 and 2.4 | Defines OI/OO/II common-neighbour and directed Adamic–Adar-style scores; proves the directed transitive-triple change-statistic identity. The identity is stated as mathematical rather than as an unperformed empirical `ttriple` fit. |
| Link, aggregation, dependence, and specification score logic | Section 2.3 | Formally defines a shared-constraint telescoping score path and distinguishes it from the implemented split-specific MPLE `L1`, `L1g`, and factorized `L2` scores. No unsupported MCMC-derived dependence result is presented. |
| Directed ERGM benchmark | Section 3 | Specifies the exponential family, conditional logit, MPLE objective, and M0–M4c structural ladder; separates conditional score availability from likelihood, goodness-of-fit, and forecasting claims. |
| Static directed LP and ERGM evidence | Table 3 and Section 6.2 | Reports predeclared directed CN, directed AA, and M1/M3/M4c rows for all four admitted static relations. These are labelled three-mask pilots and use aggregate-only inputs. |
| Formal-concept recovery | Table 3 and Section 6.2 | Reports fixed directed CN and AA rows for cap-first, arc-first concept recovery. Concepts are never described as recorded native groups. |
| Native-event missingness | Sections 4–5 and Table 4 | Primary evidence uses 30 frozen event-type masks per MCAR/MNAR-out cell for strict Enron and 30-day reconstructed MathOverflow cores. The oracle MNAR-out mechanism is defined as a stress-test construction, not an estimate of the sources’ natural missingness. |
| Orientation evaluation | Section 5.1, Table 5 | Reports the plan-defined reversal orientation accuracy with half-credit ties, on all eligible and balanced-arity subsets; keeps it separate from hard-panel PR-AUC and fixed-participant role assignment. |
| Repeated-mask uncertainty | Section 5.3 and Table 6 | Reports the four predeclared M4c `L1g` minus M0 `L1` contrasts, whole-mask bootstrap intervals, and sign-flip reference values only as within-fixed-network/mask-design evidence. |
| Bounded temporal check | Section 5.4 and Table 7 | Retains two-transition Enron/EU-core MPLE status diagnostics only. It explicitly excludes forecasting, formation/dissolution claims, and a temporal native-event competition. |
| Gate transparency | Table 8 and Sections 3.3, 6.5, and 7.4 | States the MCMC feasibility, neural reproduction, dataset-admissibility, and temporal-scope outcomes rather than filling gaps with substituted methods. |
| Privacy-preserving reproducibility | Sections 3.1 and 7.4; `manuscript/snam/tables/` | Uses only aggregate-safe tables and tracked generators. Raw records, message content, address maps, candidate panels, and candidate-level predictions remain excluded. |

## Explicit departures from the initial skeleton that are required by final Phase 2 gates

The initial skeleton was a prospective plan. The following components did **not** pass their admissibility, feasibility, or reproduction gates and are therefore not represented as successful results in the canonical manuscript:

1. **MCMC-derived joint footprint scoring (`L3`).** Enron MCMC feasibility did not meet the agreed policy. The paper reports MPLE conditional summaries and a clearly labelled supplementary score-mechanics sensitivity only; it does not label a factorized product as a joint probability.
2. **Neural/CHESHIRE comparison.** The official directed neural reproduction gate did not pass. No neural result, synthetic replacement, or claim of neural underperformance appears.
3. **Regime K and masking-plus-forecasting.** These are outside the completed Paper 1 evidence. The manuscript retains the agreed bounded temporal diagnostic only.
4. **Unadmitted sources.** Ciel remains direction-blocked and Jmail remains audit-only; neither contributes a substantive result. CAVIAR is full-static only; EU-core is restricted to dyadic/representation evidence and the temporal status check.

## Validation record

The final canonical build was run through `make manuscript-snam`; it regenerates aggregate-only tables and figures, runs BibTeX, and completes four TeX passes. Final validation found no undefined references, citation warnings, or layout warnings. The compiled preview contains 24 letter pages. A heuristic count of the main prose excluding display environments is **9,482 words**, within the project’s documented 8,000–9,500-word SNAM calibration band.
