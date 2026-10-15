# Autonomous Phase 2 execution record

**Execution date:** 2026-10-15
**Plan followed:** `ERGM_Benchmark_Directed_Link_Hyperlink_Prediction.docx`
**Repository:** `mboudour/directed_HP_LP_and_ERGMs` (private)

## Immutable input snapshot

All computations below use the exact user-supplied Google Drive archive, not a newly downloaded replacement dataset.

- Archive: `directed_hp_ergms_data_20261015.zip`
- SHA-256: `c518f2932cb389d0705f25abebf393dde9e49fc2990d881642cf40f95677305e`
- Size: 2,211,008,512 bytes
- Import record: [`docs/DATA_SNAPSHOT_IMPORT.md`](DATA_SNAPSHOT_IMPORT.md)

Raw, external, interim, and processed data remain outside Git. The aggregate results collected for this run are published separately under `results/published/` without message bodies, row-level events, candidate panels, actor identifiers, or prediction rows.

## Dataset decisions observed in the run

| Dataset | Status in this paper | Completed branch | Explicit boundary |
|---|---|---|---|
| Enron | **Primary native-event benchmark** | strict 1998–2002 custodian projection; static LP/ERGM; event-first MCAR and MNAR-out; formal concepts; factorized and bounded btergm chronological checks | Higher-order MCMLE did not pass the predeclared convergence/nonmixing gate; no higher-order MCMLE dependence result is claimed. |
| EU-core temporal | **Primary directed dyad benchmark and chronological check** | static LP/ERGM; formal-concept screen; factorized lagged check; full bounded btergm ladder | No recorded native group-event target; concept analysis remains representation-limited. |
| CAVIAR full matrix | **Static directed benchmark** | direction-gated full matrix; static LP/ERGM; formal-concept screen | Phase sequence is excluded: CAVIAR7 has a duplicate actor label and direction/longitudinal interpretation is not generalized to the phases. |
| MathOverflow | **Reconstructed native-event benchmark** | approved 30-day question–answer reconstruction; static LP/ERGM; event-first masks, random and hard panels, native-event ERGM footprint scores | A reconstructed answerer-to-asker group is not an observed multi-recipient event; it is labelled as reconstructed throughout. |
| Ciel | **Excluded** | source/direction audit only | Matrix orientation is not sufficiently supported by the available source record. |
| Jmail v1 | **Excluded** | provenance and admissibility audit only | It remains unapproved for the present paper; no predictive results are reported. |

## Completed computation inventory

All static ladders use the agreed directed terms `M0`–`M4c`, fixed decay 0.5, and MPLE. Static conditional-score runs use the frozen three-replicate 30% MCAR arc-first masks and score only held-out candidate dyads. Native-event runs use frozen three-replicate MCAR and three-replicate MNAR-out event-type masks.

| Result family | Enron | EU-core | CAVIAR | MathOverflow |
|---|---:|---:|---:|---:|
| Static directed arc LP pilot | completed | completed | completed | completed |
| Static ERGM ladder (`M0`–`M4c`) | 6/6 fitted | 6/6 fitted | 6/6 fitted | 6/6 fitted |
| Masked conditional ERGM scorer | 12/12 scored | 12/12 scored | 12/12 scored | 12/12 scored |
| Cap-3 formal-concept audit | completed | completed | completed | completed |
| Native-event fidelity and event-first evaluation | completed | not applicable | not applicable | completed |
| Native-event ERGM footprint scoring | 24/24 model–split runs scored | not applicable | not applicable | 24/24 model–split runs scored |
| Lagged chronological check | completed | completed | not applicable | not applicable |
| Bounded btergm ladder | 3 fitted; 2 nonfinite | 5/5 fitted | not applicable | not applicable |

## Temporal check results

The temporal section is a **bounded chronological check**, not a forecasting study. It uses three consecutive panels, two response transitions, and 20 btergm bootstrap replications.

- **EU-core:** all five models (`T_tt`, `T0`, `T1`, `T2`, and `T2_minus_H`) produced finite MPLE coefficient sets. The factorized lagged-only baseline has a positive lagged shared-outgoing-neighbour coefficient of 0.2951 (odds ratio 1.3433); this is a conditional historical association, not a forecast claim.
- **Enron:** `T_tt`, `T0`, and `T1` produced finite coefficient sets. `T2` and `T2_minus_H` were retained as `fit_nonfinite_coefficients`, signalling separation/numerical identification on the sparse three-month panel. The output is retained as an important feasibility boundary, rather than being replaced by a different specification.

## Interpretation guardrails preserved

1. The static and btergm models are **conditional-score estimators** in this implementation; they are not forecasts, STERGMs, or relational hyperevent models.
2. MPLE results are not treated as MCMLE convergence, simulation goodness-of-fit, or coefficient-inference evidence.
3. Formal concepts are derived from an aggregate graph. They are never relabelled as observed Enron or MathOverflow group events.
4. The native-event `L2` product of conditional pseudolikelihood scores is not the plan's matched-marginal joint `L2`; only the separately gated conditional simulation addresses that distinction.
5. All high-level findings are pilot results with exactly the fixed replicate counts stated above. They do not establish significance or generalize to unbalanced population prevalence.

## Reproducibility

- Python environment: `uv.lock`; execute with `uv sync --extra dev`.
- R environment: project-local `renv.lock`; initialize with `Rscript r/bootstrap_renv.R`.
- Source-level regression suite: `make test` and `make r-model-test`.
- Aggregate published results: `results/published/phase2_20261015/`.

The aggregate bundle records file SHA-256 values and the source-bundle paths from which each non-sensitive result table was copied.
