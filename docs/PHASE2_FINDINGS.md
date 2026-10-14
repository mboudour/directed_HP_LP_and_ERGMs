# Phase 2 empirical findings log

This versioned log records observed pilot results and their permitted interpretation. It is not a substitute for the final manuscript tables.

## 2026-10-14 — EU-core cap-3 formal-concept screening audit

**Input.** The prepared EU-core core-100 directed graph contains 100 fixed nodes and 2,682 binary directed arcs. The deterministic audit enumerated formal concepts with cap-first bounds `|T| <= 3` and `|H| <= 3`.

**Observed result.** The capped section contains 45 concepts: one `(2,2)`, nine `(2,3)`, 11 `(3,2)`, and 24 `(3,3)`. Every emitted concept is nontrivial, and none has a node in both tail and head roles. Their union covers 225 of 2,682 observed arcs (8.389%). Per-arc concept multiplicity is zero at the minimum and median, one at the 95th percentile, and five at the maximum.

**Interpretation recorded for Phase 2.** EU-core remains eligible for directed arc-level comparisons, static ERGM/MPLE checks, and the bounded chronological dependence analysis. It is not promoted to a primary source for broad concept-recovery claims: the cap-3 formal-concept section is small and covers a limited portion of the static relation. Any EU-core footprint/concept analysis must be labelled exploratory, representation-dependent, and restricted to its explicit candidate set. It never supports native-event recovery in the primary design.

**Evidence.** Local result bundle: `results/phase2/eu_core_formal_concepts_tail3_head3/`; its `summary.md` and `arity_distribution.csv` contain the displayed counts. The result is generated locally and deliberately excluded from Git because it is derived data.

## 2026-10-14 — Enron primary timestamp inclusion policy

**Input.** The address-level native-event candidate audit covers 490,141 timezone-aware events. Its raw header timestamps occur in 14 calendar years between 1980 and 2044. The bulk is contiguous in 1998–2002: 168 events in 1998, 10,896 in 1999, 191,945 in 2000, 252,755 in 2001, and 33,988 in 2002. The seven isolated years outside this period total 389 events.

**Decision.** The primary Enron custodian projection and all derived monthly panels will retain the inclusive UTC interval `1998-01-01T00:00:00+00:00` through `2002-12-31T23:59:59.999999+00:00`. This preserves 489,752 events (99.920635%) and excludes 389 events (0.079365%) from isolated, non-contiguous years. The small 1998 segment is retained rather than discarded as a possible valid boundary period.

**Boundary.** This resolves the timestamp-only gate. The related identity and projection policy was subsequently approved below; its materialized local map and projected outputs still require a reproducible build.

**Evidence.** Versioned policy: `configs/enron_temporal_policy.yaml`; locally generated profile: `data/metadata/enron_20150507_event_timestamp_profile.json`, `data/metadata/enron_20150507_event_timestamp_year_counts.csv`, and `docs/data_audits/enron_20150507_event_timestamp_profile.md`.

## 2026-10-14 — Enron strict primary custodian projection

**Decision.** The researcher approved the strict primary policy. It automatically accepts only custodian-address mappings with a unique rank-one sent-folder candidate, at least 90% support, and no rank-one address shared by another custodian. The previous audit implies 110 automatic mappings and 40 excluded/unresolved custodians.

**Event rule.** A primary Enron native event must have an approved mapped sender and approved mapped identities for every `To`/`Cc` recipient. If any participant is unmapped, the entire event is excluded. A recipient mapping to the sender's custodian is removed. Distinct maildir records are retained after the raw-SHA and Message-ID duplicate audits.

**Why strict.** This preserves complete internally observed recipient heads among the approved custodian universe. A clipped-head alternative could retain more internal ties, but it would censor members of the group event and therefore create a projected-event, rather than native-event, target.

**Observed build result.** The rule materialized 110 approved custodian identities. It retained 7,881 complete strict custodian-level native events from 490,141 address-level candidates (1.607905%), after excluding 389 events outside the approved 1998–2002 range and 481,871 events with one or more unmapped participants. The 100-node activity-ranked core retains 7,820 events (99.225987% of projected events), 635 of 9,900 possible directed static arcs (6.414141% density), and 38 nonempty calendar-month panels.

**Interpretation recorded for Phase 2.** The Enron **data-preparation and primary-input gate passes**: the strict result has more than the required 100 actors, thousands of complete recorded internal events, a non-degenerate directed core graph, and a longitudinal monthly panel. The severe event loss is an explicit consequence of preserving fully observed recipient heads within the approved custodian universe; it must be reported as a selection boundary, not described as a full Enron communication system. The retained object is a conservative internal-custodian native-event benchmark.

**Implementation status.** `scripts/15_materialize_enron_strict_mapping.py` creates the ignored, address-bearing local map and non-sensitive gate metadata. `scripts/25_build_enron_custodian_projection.py` creates the local primary event, core-100 arc, and monthly-panel objects. Local evidence: `data/metadata/enron_20150507_custodian_projection.json` and `docs/data_audits/enron_20150507_custodian_projection.md`.

## 2026-10-14 — Enron cap-3 formal-concept screening audit

**Input.** The approved strict Enron core has 100 fixed custodian nodes and 635 binary directed arcs. The deterministic audit enumerated directed formal concepts with cap-first bounds `|T| <= 3` and `|H| <= 3`.

**Observed result.** The capped section has 232 concepts, all with at least one role of arity greater than one, and none with a node in both tail and head roles. It covers 551 of 635 directed arcs (86.771654%), leaving 84 arcs outside the capped concept footprints. The concepts generate 1,409 footprint-arc occurrences: an average footprint size of 6.073276 arcs and 2.557169 concept memberships per covered arc. Arc membership has minimum zero, median two, 95th percentile five, and maximum ten.

**Arity composition.** The section contains 1 `(1,2)`, 8 `(1,3)`, 4 `(2,1)`, 46 `(2,2)`, 52 `(2,3)`, 5 `(3,1)`, 60 `(3,2)`, and 56 `(3,3)` concepts. Thus 92.241379% of concepts have at least two nodes in both roles; the section is not driven by one-to-many or many-to-one stars.

**Interpretation recorded for Phase 2.** The Enron **cap-3 representation gate passes** for the main paper. Unlike EU-core's cap-3 section, Enron offers a substantial, high-coverage derived concept section with moderate and explicitly measurable footprint overlap. It is therefore eligible for the paper's exploratory formal-concept and footprint recovery targets as well as its primary recorded-native-event target. Formal concepts remain algebraically derived structures, not observed email groups; all reporting must retain this distinction. The cap-3 audit is the computationally bounded primary screen, not an assertion that larger caps are unneeded or that this is the final sensitivity analysis.

**Evidence.** Local result bundle: `results/phase2/enron_formal_concepts_tail3_head3/`, especially `summary.md`, `arity_distribution.csv`, and `arc_multiplicity.csv`.

## 2026-10-14 — Enron full-network static ERGM ladder feasibility check

**Observed result.** Every plan-aligned MPLE specification (`M0` through `M4c`) fit successfully with no recorded warnings or unavailable terms. The supplied strict core has 100 nodes, 635 of 9,900 possible directed arcs (6.414141% density), 217 reciprocal pairs, and a reciprocated-arc fraction of 68.346457%.

**Interpretation recorded for Phase 2.** This passes the **static ERGM software and structural-feasibility gate** for Enron: the directed degree, mutuality, OTP, OSP, ISP, and cyclic-triple terms can all be evaluated on the stated core. It is not evidence of model adequacy or a prediction result. The fits are MPLE, so they do not provide MCMLE convergence or simulation goodness-of-fit evidence; coefficient interpretation remains separate from masked score evaluation.

**Evidence.** Local result bundle: `results/models/enron_static_ladder_plan/`, especially `model_status.csv`, `network_summary.csv`, `coefficients.csv`, and `diagnostics.txt`.

## 2026-10-14 — Enron masked conditional ERGM arc-score pilot

**Design.** Three deterministic, 30% arc-first MCAR masks of the strict Enron core-100 were generated from the fixed pilot seed. `M0`, `M1`, `M3`, and `M4c` were each fitted only to their corresponding masked training graph, then used to produce exact conditional ERGM probabilities for that replicate's balanced held-out-arc/true-nonedge panel. All 12 model-replicate fits and scores completed.

| Model | Accuracy | Precision | Recall | F1 | Matthews | ROC-AUC | PR-AUC | Log loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M0 | 0.5000 | — | 0.0000 | 0.0000 | — | 0.5000 | 0.5000 | 1.5741 |
| M1 | 0.5000 | — | 0.0000 | 0.0000 | — | 0.7263 | 0.7184 | 1.1741 |
| M3 | 0.6325 | 0.9867 | 0.2684 | 0.4216 | 0.3861 | 0.9190 | 0.9242 | 0.9623 |
| M4c | 0.6281 | 0.9864 | 0.2596 | 0.4110 | 0.3788 | 0.9186 | 0.9243 | 0.9636 |

Values are means over three replicates. The output retains their SDs and every metric status in the local score bundle.

**Interpretation recorded for Phase 2.** Adding mutuality (`M1`) improves threshold-free ranking relative to density alone (ROC-AUC `+0.2263`, PR-AUC `+0.2184`) but yields no 0.5-threshold positive classifications because fitted conditional probabilities remain below 0.5. Adding degree heterogeneity and outgoing-two-path closure (`M3`) produces the material score lift: relative to `M1`, ROC-AUC rises `+0.1927`, PR-AUC `+0.2058`, and log loss falls `-0.2118`; its 0.5-threshold precision is 0.9867 but recall is 0.2684. The more complex closure-plus-cycle model `M4c` supplies no meaningful improvement over `M3` in this three-replicate pilot: its PR-AUC difference is `+0.0001`, while ROC-AUC, F1, Matthews correlation, and log loss are slightly worse. `M3` is therefore the current parsimonious candidate for this **static arc-level conditional-score** task, pending the preregistered larger experiment and target-specific evaluations.

**Caution.** The 0.5 threshold is a fixed diagnostic, not an optimized decision rule. The candidate panel is deliberately balanced, whereas the full graph is sparse; threshold-dependent metrics and log loss are therefore panel-specific and must not be generalized to a deployment prevalence. The three replicates quantify only the fixed-split Monte Carlo variation and do not establish statistical significance.

**Evidence.** Local result bundle: `results/models/enron_masked_ergm_plan/`, especially `summary.md`, `metrics.csv`, `model_status.csv`, `replicate_status.csv`, and `conditional_predictions.csv`.

## 2026-10-14 — Enron native-event versus formal-concept fidelity audit

**Design.** The audit compares recorded strict Enron core events with the cap-first `(|T|, |H|) <= (3, 3)` formal-concept section of the same 100-node, 635-arc relation. Repeated message records are grouped into exact tail/head event types while retaining their occurrence counts. The cap retains 7,793 of 7,820 core event records (99.654731%) and produces 719 native event types; the derived section has 232 formal concepts.

**Observed result.** There are **zero exact tail/head matches**: formal-concept precision against recorded event types and native-event-type recall by concepts are both 0. The two representations nevertheless have substantial dyadic agreement: their footprint intersection contains 544 arcs, their union contains 635, and their footprint Jaccard is 0.856693. The formal concepts cover 544 of 628 capped-native-event footprint arcs (86.624204%), while capped native events cover 544 of 551 formal-concept footprint arcs (98.729583%).

**Cover diagnostics.** Every one of the 232 formal concepts has at least two contributing recorded event types, and all 232 lack an exact recorded-event type. No native event type contains two or more formal-concept footprints under the audit's strict containment definition. Thirty-six of 719 (5.006954%) best native-event-to-concept matches exhibit a role distortion, meaning that at least one actor occurs in the opposite role in the best derived match.

**Interpretation recorded for Phase 2.** This is a direct empirical demonstration of the paper's target ladder and non-identifiability claim. **High footprint overlap does not imply event recovery:** the aggregate dyadic relation is sufficiently shared to support concepts and their footprints, but it does not retain a recorded sender–recipient group as an exact formal concept. Enron must therefore report native-event recovery, concept recovery, and footprint completion as separate targets; concept scores must never be presented as recovering an email event. At the same time, the cap retains almost all core message records, so the native-event target itself remains viable for event-first evaluation. This first fidelity audit is descriptive; a degree-preserving-rewiring comparison remains required before making chance-corrected fidelity claims.

**Evidence.** Local result bundle: `results/phase2/enron_native_event_fidelity_tail3_head3/`, especially `summary.md`, `summary.json`, `event_to_concept_matches.csv`, and `concept_to_event_aggregation.csv`.
