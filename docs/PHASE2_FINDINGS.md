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

## 2026-10-14 — Enron primary event-first native-event-type masks

**Design.** The six fixed pilot splits sample the 719 cap-eligible strict Enron tail/head event types, holding out every repeated message record of each selected type. The observed arc graph is reconstructed solely from the observed types. Three MCAR splits use fixed-count sampling; three MNAR-out splits use the plan's oracle inclusion probabilities proportional to full-data sender activity. The requested type-level masking rate is 0.30 in both mechanisms.

| Mechanism | Mean type rate | Mean record rate | Mean arc-removal rate | Mean held-out types with an already observed complete footprint |
|---|---:|---:|---:|---:|
| MCAR | 0.2990 | 0.2908 | 0.2336 | 0.2977 |
| MNAR-out | 0.3009 | 0.4988 | 0.2277 | 0.1789 |

**Observed result.** Both mechanisms achieve the intended approximately 30% **event-type** masking rate. The activity-biased MNAR-out design removes 20.80 percentage points more message records on average than MCAR (49.88% versus 29.08%) but a slightly smaller proportion of distinct projection arcs (22.77% versus 23.36%). The mean fraction of held-out types whose full footprint survives through other observed types is 29.77% under MCAR and 17.89% under MNAR-out. On average, MCAR causes 71.67 nodes to lose at least one outgoing arc and 75.00 to lose an incoming arc; MNAR-out concentrates outgoing losses in fewer nodes (42.67) while producing a comparable number of incoming-loss nodes (73.33).

**Interpretation recorded for Phase 2.** The realised-rate reporting works as intended and shows why nominal 30% masking cannot be used as a common severity label across mechanisms. Event recurrence and dyadic projection create substantial survival of held-out native-event footprints, especially under MCAR. The MNAR-out stress test targets high-activity senders, causing much greater record-level loss but similar distinct-arc loss and more concentrated outgoing disruption. Every event-first result must therefore report the type, record, and arc realised rates, the already-observed-footprint baseline, and its mechanism separately. These masks are valid inputs for native-event, footprint, and role-assignment scoring; they contain no candidate negatives or predictive scores themselves.

**Evidence.** Local result bundle: `results/phase2/enron_event_first_type_masks/`, especially `summary.md`, `split_summary.csv`, the top-level `manifest.json`, and each split's `heldout_event_types.csv`, `observed_event_types.csv`, `observed_arcs.csv`, `removed_arcs.csv`, and `removal_strata.csv`.

## 2026-10-14 — Enron event-first native-event heuristic pilot

**Design.** Each of the six frozen event-first splits was evaluated on a leakage-safe, 1:1 random negative panel of non-event types exactly matched to each positive's tail and head arities. Every candidate's participants had to be pairwise within weak distance two in that split's observed projection. All observed and held-out native event types were excluded from the negative pool. The uncalibrated scores are lifted arithmetic means across the candidate footprint of reverse-arc, degree-product, directed common-neighbor, and directed Adamic–Adar components; the already-observed-footprint indicator is a descriptive baseline, not a predictor.

**Candidate coverage.** The candidate universe retains a mean 93.9535% of held-out native types under MCAR (minimum 91.6279%) and 95.6489% under MNAR-out (minimum 92.3810%). The excluded held-out types are reported per split rather than relabelled or replaced.

| Mechanism | Score | ROC-AUC | PR-AUC | Precision@k / recall@k |
|---|---|---:|---:|---:|
| MCAR | Already-observed-footprint baseline | 0.6511 | 0.6444 | 0.5907 |
| MCAR | Reverse-arc mean | **0.7800** | 0.7589 | 0.7158 |
| MCAR | Total directed Adamic–Adar mean | 0.7752 | **0.7988** | **0.7234** |
| MCAR | Total common-neighbor mean | 0.7575 | 0.7718 | 0.7005 |
| MNAR-out | Already-observed-footprint baseline | 0.5786 | 0.5677 | 0.5445 |
| MNAR-out | Reverse-arc mean | **0.8078** | **0.7884** | **0.7474** |
| MNAR-out | II Adamic–Adar mean | 0.7707 | 0.7854 | 0.7148 |
| MNAR-out | Total common-neighbor mean | 0.6997 | 0.7111 | 0.6451 |

Values are means over three replicates; replicate SDs remain in the local summary. In this 1:1 panel, `k` equals the number of positives, so precision@k and recall@k are numerically identical by construction.

**Interpretation recorded for Phase 2.** The surviving-footprint baseline is informative but not sufficient: under MCAR, the total directed Adamic–Adar score improves on it by `+0.1241` ROC-AUC and `+0.1544` PR-AUC; under MNAR-out, reverse arcs improve on it by `+0.2292` ROC-AUC and `+0.2207` PR-AUC. Reciprocity is the leading single native-event signal in both mechanisms, while the combined directed Adamic–Adar score is strongest by PR-AUC under MCAR. Under MNAR-out, the II Adamic–Adar component is competitive with reverse arcs in PR-AUC, but three replicates do not resolve their difference. The results are descriptive ranking evidence for this **random, arity-matched case-control panel only**; they do not establish calibrated event probabilities, performance at native prevalence, robustness across mechanisms, or results on the planned hard-negative panels.

**Evidence.** Local result bundle: `results/phase2/enron_event_first_native_heuristics/`, particularly `summary.md`, `metric_summary.csv`, `split_summary.csv`, each split's `candidate_predictions.csv` and `metrics.csv`, and the top-level `manifest.json`.

## 2026-10-14 — Enron directed native-event hard-negative pilot

**Design.** The same six frozen event-first splits support two separate 1:1 hard panels. `reversal_orientation` contrasts a held-out `(T,H)` native event type with `(H,T)` only when the reversal is an unseen native event type. `role_exchange` exchanges one tail actor with one head actor while preserving the actor set and both role arities, again requiring the transformed group to be an unseen native event type. Both require the split-specific weak-two-hop candidate universe. No unavailable positive was replaced by an easy random negative.

**Panel coverage.** Of the candidate-eligible held-out types, valid reversal pairs cover 276 of 606 (45.5446%) under MCAR and 281 of 621 (45.2496%) under MNAR-out. Valid role-exchange pairs cover 260 of 606 (42.9043%) under MCAR and 252 of 621 (40.5797%) under MNAR-out. Hence these are deliberately difficult but selected subsets of the full native-event target; coverage must accompany every reported hard-panel metric.

| Panel | Mechanism | Most discriminating score | ROC-AUC | PR-AUC | Reading |
|---|---|---|---:|---:|---|
| Reversal/orientation | MCAR | Degree-product mean | 0.5667 | 0.5707 | Small lift over the footprint baseline; no strong orientation discrimination. |
| Reversal/orientation | MNAR-out | Reverse-arc mean | 0.6147 | 0.5823 | Clearer but still modest directional signal. |
| Role exchange | MCAR | Degree-product mean | 0.5779 | 0.5762 | Small discrimination after preserving actor set and role arities. |
| Role exchange | MNAR-out | Reverse-arc mean | 0.5571 | 0.5497 | Modest signal; II Adamic–Adar has a similar PR-AUC (0.5515). |

**Observed structure.** Several shared-neighbor components are exactly or close to chance in the reversal panel—II and OO have ROC-AUC 0.5000 in both mechanisms—consistent with their role-symmetry for this particular transformed contrast. Under MCAR, the reverse-arc mean is below chance in both hard panels (reversal ROC-AUC 0.4465; role-exchange ROC-AUC 0.4455), whereas under MNAR-out it becomes the strongest or near-strongest directional score. The mechanism-dependent sign and modest three-replicate effects require reporting the complete score table, rather than selecting a single favorable hard-panel result.

**Interpretation recorded for Phase 2.** The random-panel performance does **not** transfer wholesale to directed role discrimination. The hard panels show that native-event recovery requires a genuinely directional and role-sensitive evaluation: a score that ranks random true non-events well can be near chance, or even anti-ranked, when the comparator preserves the same participants or reverses their roles. These panels therefore pass as valid target-specific stress tests and motivate the planned ERGM score comparison; they do not yet establish a stable preferred heuristic or a general role-recovery claim.

**Evidence.** Local result bundle: `results/phase2/enron_event_first_native_hard_panels/`, particularly `summary.md`, `split_summary.csv`, `metric_summary.csv`, each split's panel-specific `candidate_predictions.csv` and `metrics.csv`, and the top-level `manifest.json`.

## 2026-10-14 — Enron native-event ERGM conditional footprint-score pilot

**Design.** The six frozen event-first splits were used unchanged. For each split, `M0`, `M1`, `M3`, and `M4c` were independently fit by MPLE to the split-specific observed dyadic projection; no full-network coefficients were reused. Exact single-dyad conditional-pseudolikelihood ERGM scores were then aggregated over each predeclared native-event candidate footprint as `L1` (arithmetic mean), `L1g` (geometric mean), and a factorized `L2` product. The random, reversal/orientation, and role-exchange panels retain their own candidate universes and are evaluated separately using ROC-AUC, PR-AUC, precision@k, and recall@k only.

**Completion result.** All 24 model/split combinations completed: four models for each of six frozen splits. No split or model failure was reported. This is a software-and-data-contract success, not MPLE goodness-of-fit evidence.

| Panel | Mechanism | Best pilot specification/score by ROC-AUC | ROC-AUC | PR-AUC | Reading |
|---|---|---|---:|---:|---|
| Random | MCAR | M4c / L1g | **0.8509** | 0.8648 | Strong footprint ranking; closure and cycle terms add a modest lift over M3. |
| Random | MNAR-out | M3 / L1g | **0.8195** | 0.8422 | Strong ranking under the activity-biased stress split; M4c has slightly higher PR-AUC (0.8460) but lower ROC-AUC. |
| Reversal/orientation | MCAR | M4c / L1 | 0.4732 | 0.4907 | Near-chance to anti-ranked; random-panel gains do not transfer to role reversal. |
| Reversal/orientation | MNAR-out | M1 / L2 | **0.6395** | 0.5895 | Modest directional separation; the mutuality-only factorized footprint score is strongest by ROC-AUC. |
| Role exchange | MCAR | M4c / L2 | 0.4743 | 0.4866 | Near-chance to anti-ranked after preserving actor set and role arities. |
| Role exchange | MNAR-out | M1 / L2 | **0.5988** | 0.5590 | Small but positive role-sensitive separation; later closure terms do not improve it. |

**Nested comparison.** On random panels, M1 alone is already informative because reciprocal ties are common: its L1 ROC-AUC is 0.7800 under MCAR and 0.8078 under MNAR-out, exactly matching the reverse-arc heuristic's ranking in this pilot. Under MCAR, M3/L1g raises ROC-AUC by `+0.0626` over M1 and M4c/L1g by `+0.0709`; their PR-AUCs are 0.8569 and 0.8648, respectively, compared with 0.7589 for M1. Under MNAR-out, the lift is smaller: M3/L1g is `+0.0117` ROC-AUC over M1 and M4c/L1g is `+0.0109`. This coherence is expected because M1 varies principally with the same reciprocal-dyad information captured by the reverse-arc heuristic; it is a useful implementation cross-check, not independent evidence.

**Interpretation recorded for Phase 2.** The static directed ERGM ladder supplies a clear **factorized graph-footprint** ranking lift over density and mutuality in the random, arity-matched native-event panel. The higher-order terms do not yield a stable role-recovery result: both MCAR hard panels remain below chance for every model/score combination, while MNAR-out produces only modest M1-driven separation. This strengthens the earlier target-ladder conclusion: good dyadic-footprint completion does not constitute recovery of a recorded email event or correct sender/recipient roles. The reported `L2` is a product of single-dyad conditional-pseudolikelihood scores. It is **not** the matched-marginal `L2` in the plan’s dependence identity, because it does not place every unknown arc of a candidate footprint under one shared observation constraint. The subsequent MCMLE conditional-simulation workflow supplies this matched `L2` and `L3-F`. No native-event probability, exact event recovery, joint footprint probability, formal-concept score, coefficient inference, or MPLE goodness-of-fit conclusion may be drawn from this pilot.

**Evidence.** Local result bundle: `results/models/enron_native_event_ergm_footprints/`, specifically `summary.md`, `metric_summary.csv`, `ranking_metrics.csv`, `event_footprint_scores.csv`, `model_status.csv`, `split_status.csv`, `network_summary.csv`, and `run_manifest.json`. The inputs are preserved locally in `results/phase2/enron_native_event_ergm_inputs/` and derive exclusively from the six frozen event-first split/panel artifacts.

## 2026-10-14 — Enron conditional joint-footprint MCMLE smoke test

**Technical completion.** The initial one-split M1 smoke test completed on
`mcar_replicate_001`: the split-specific `edges + mutual` MCMLE fit converged
within four iterations, all six sampled candidate calculations returned, and no
joint Monte Carlo estimate was zero. The unavailable `Rglpk` solver caused a
visible fallback to `lpSolveAPI`; Statnet reports this as suitable for the
small two-parameter fit. The deliberately disabled likelihood normalizing
constant is reflected by the expected message that AIC/BIC were not estimated.

**Crucial limitation discovered.** The random sampler selected six singleton
`(1,1)` footprints. Therefore, for every candidate, `L1 = L1g = L2 = L3-F` and
`delta_dep = 0` (up to floating-point roundoff) by arithmetic: one unknown dyad
has no within-footprint joint dependence to estimate. This confirms that the
candidate-specific observation constraint and conditional-simulation software
path work locally. It is **not** evidence that M1 factorizes over a multi-dyad
footprint, and it provides no result about M4 dependence.

**Corrective design and result.** The revised target required exactly two
unobserved footprint dyads, with both reverse arcs observed, and obtained one
eligible role-exchange negative candidate:
`mccarty-d → {corman-s, hayslett-r}`. Its M1 fit had `edges = -3.81160` and
`mutual = 4.11895`. Because neither unknown dyad is the reverse of the other,
the M1 conditional distribution factorizes for this candidate; the fitted
probability for either dyad conditional on its observed reverse is
`logit^{-1}(-3.81160 + 4.11895) = 0.57624`, with exact product `0.33205`.
The conditional-simulation estimates were `L2 = 0.32725`, `L3-F = 0.35500`,
and `delta_dep = 0.08139`; their raw difference is `0.02775`, only `0.82` of
the reported (naive) `L3-F` Monte Carlo SE `0.03384`. This is fully compatible
with the factorization expected under M1 and is **not** dependence evidence.

**Precision correction.** That run used one sequential MCMC chain, so the
printed binomial SE can understate uncertainty if draws are autocorrelated.
The driver now restarts each completion from the same candidate-specific
observed basis (`sequential = FALSE`), allowing the smoke-test binomial SE to
have its stated interpretation. The completed sequential-chain run remains
valid as an end-to-end software test and qualitative M1 check, but is not used
as a quantified dependence estimate. The independent-chain rerun is still
small; no M4/multi-split calculation follows automatically.

**Interpretation boundary.** This single selected candidate is a negative
role-exchange example, so it cannot evaluate discrimination. It validates only
the M1 matched-observation `L2`/`L3-F` mechanism. The MCMLE diagnostic output
contains no immediate red flag, but no GOF conclusion is made and no M4
dependence conclusion is available.

**Independent-chain confirmation.** Repeating the same M1 calculation with
each of 200 conditional completions independently restarted from the identical
candidate-specific observed basis returned `L2 = 0.336175`, `L3-F = 0.350000`,
and `delta_dep = 0.040301`; the raw gap is `0.013825`, versus a binomial
`L3-F` Monte Carlo SE of `0.033727`. This again agrees with the expected M1
factorization. The code now additionally saves each conditional dyad state and
calculates a bootstrap uncertainty interval for `delta_dep`; that extension is
used for the subsequent one-candidate M4 calibration rather than recasting this
M1 confirmation as a substantive result.

### Enron M4 MCMLE feasibility gate — failed without a usable fit

The one-candidate M4 conditional-simulation attempt was intentionally stopped
after `9:22` of CPU time. The interruption occurred during adaptive MCMC
sampling in MCMLE iteration 5. Iterations 1–4 were not within the convergence
tolerance region; the MCMC sampling work became progressively slower, with the
last displayed estimated time remaining exceeding five minutes. No M4 fit,
candidate score, coefficient table, or dependence conclusion was produced.

**Decision.** This is an M4 MCMLE mixing/convergence failure on the current
100-node Enron pilot specification, **not** evidence of a local-computer fault
and not a reason to keep increasing interactive waiting time. The MCMLE target
is retired for this pilot. The next bounded calculation is an explicitly marked
M4 MPLE parameter-plug-in conditional-simulation sensitivity, using the same
two-dyad candidate and independent conditional chains. It can validate score
mechanics under closure terms but cannot substitute for a converged MCMLE result.

### Enron M4 MPLE joint-footprint sensitivity — completed, technical result only

On the same preselected two-dyad role-exchange negative candidate used for the
M1 factorization check, the M4 **MPLE parameter-plug-in** fit completed in
6.2 seconds. The two conditional simulation marginals gave `L2 = 0.412800`.
The joint conditional completion frequency was `L3-F = 0.520000`, producing an
absolute gap of `0.107200` and `delta_dep = 0.230866`. The 1,000-resample
bootstrap Monte Carlo interval for `delta_dep` was `[0.153023, 0.309244]`,
equivalent to a joint/product ratio of `1.260` with interval `[1.165, 1.362]`.

**Interpretation.** Unlike M1, the M4 parameter vector induces a clear positive
within-footprint association in this bounded conditional calculation. This
validates the score-gap machinery under the closure-capable specification and
supports its substantive rationale. It is **not** evidence that the final M4
MCMLE model has been estimated successfully: the MCMLE gate above remains
failed, the candidate is one selected negative, and no discrimination or
population-level conclusion follows.

### Enron M2 MCMLE feasibility gate — failed nonmixing check

The core-100 M2 MCMLE run ended after 7.4 seconds but did not produce a fitted
model. After three non-converged iterations, it printed `Post-burnin sample is
constant; returning.` and then terminated with the decisive error:
`Unconstrained MCMC sampling did not mix at all. Optimization cannot continue.`
The output `model_status.csv` records `fit_failed`, zero candidates scored, and
no diagnostics or fitted model object. The `Rglpk` fallback notice is unrelated
to this failure.

The plan requires non-degenerate simulation before scaling, so M2 does **not**
pass the MCMLE feasibility gate and no score from this attempted fit is used.
The joint-score driver now captures a constant post-burn-in sample and blocks
scoring with status `mcmle_gate_failed_nonmixing` if Statnet returns an object
instead of the explicit error seen in this run.

**Consequence.** On this 100-node Enron split, M1 is a valid MCMLE factorization
diagnostic, whereas M2 fails by complete nonmixing and M4 fails its
convergence/mixing gate. No additional MCMLE ladder fit is launched until a
model-revision or reduced-core policy is chosen explicitly.

### Approved response — deterministic nested Enron core-50 MCMLE feasibility module

The researcher approved a fixed, nested core-50 for MCMLE feasibility and
conditional joint-score sensitivity only. It is defined as primary strict
core-100 ranks 1–50 under the already frozen sent-plus-received activity rule;
there is no reranking, model-based choice, or tuning. It retains the same
strict 1998–2002 range, custodian map, full-event participant rule, and
message-copy policy. All primary masking, heuristic, MPLE, formal-concept, and
native-event results remain core-100 results.

The core-50 exists to test whether M2/M3/M4 MCMLE can satisfy the convergence
and non-degeneracy gate at a transparently smaller scale. A success does not
erase or replace the core-100 M2/M4 failures. The precise selection and scope
are documented in `docs/ENRON_MCMLE_FEASIBILITY_CORE.md`.

**Materialization result.** The nested core-50 contains 6,168 all-participant
recorded events (78.874680% of the primary core-100 event count), 287 static
directed arcs (45.196850% of the primary arc count), and a binary directed
density of 11.714286%. It therefore retains substantial repeated-event and
dyadic structure while reducing the state space from 9,900 to 2,450 possible
nonloop dyads. It is adequate for the approved bounded feasibility module;
its mask, candidate-panel, and joint-score inputs remain entirely separate
from the core-100 bundles.

**Input preparation result.** The core-50 event-first pipeline completed six
frozen splits (three MCAR and three MNAR-out). It contains 6,164 cap-eligible
event records, 351 cap-eligible ordered tail/head event types, and 286
cap-eligible projection arcs. Random, reversal/orientation, and role-exchange
candidate panels were exported for every split to the isolated joint-score
bundle. This confirms that the selected feasibility core supports the same
candidate contract as the primary benchmark; it does not produce a primary
prediction result.

**Prefit correction.** The first core-50 M2 command stopped before fitting an
ERGM: under the deliberately strict rule of exactly two unknown footprint arcs
*and* an observed reverse for each, `mcar_replicate_001` selected zero
candidates. The joint driver then exposed an empty-table concatenation bug.
That bug is corrected, and a privacy-preserving aggregate candidate-eligibility
audit now precedes every MCMC run. This is neither an M2 fit failure nor a
nonmixing result; it is a selection-contract issue that must be resolved from
the frozen panels before M2 is attempted.

**Candidate-audit decision.** Across the six frozen core-50 splits, 193 of
1,980 candidate footprints have exactly two unknown dyads and 54 additionally
have observed reverse arcs for both. The initial `mcar_replicate_001` has seven
exact-two candidates but zero satisfying the reciprocal condition. The earliest
MCAR split with a nonempty strict class is `mcar_replicate_002` (15 exact-two,
five strict). The bounded M2 gate is therefore fixed to
`mcar_replicate_002`, retaining the reciprocal two-dyad rule rather than
relaxing it. This availability rule was chosen before any M2 fit or score.

### Enron core-50 M2 MCMLE feasibility gate — failed nonconvergence

The bounded M2 run on the preselected `mcar_replicate_002` strict class began
with MPLE and proceeded through all five permitted MCMLE iterations in 8.251
seconds. The estimating equations remained outside the tolerance region. In
iteration 3, Statnet reported a convergence-test p-value of 0.9292 and increased
the sample size; after iteration 4, it reported that the equations had not moved
closer to the tolerance region more than once in four steps. It then terminated
the bounded fit with `MCMLE estimation did not converge after 5 iterations.`

Three candidates had been selected for conditional scoring, but the gate
correctly produced zero scores and saved no fitted-model or diagnostic object.
This is **nonconvergence within the predeclared bounded fitting budget**, not a
claim that the chain mixed poorly, a computer fault, or proof that a longer or
retuned MCMLE run could never converge. The prior generic status label has been
corrected in the code: future instances of this message are recorded as
`mcmle_gate_failed_nonconvergence`, distinct from a constant-sample or explicit
MCMC-nonmixing failure.

**Decision.** The deterministic core-50 does not pass the M2 MCMLE feasibility
gate. No M3 or M4 MCMLE fit follows under this paper's bounded-computing policy,
and no retry with altered tuning or a longer iteration budget will be launched
without an explicitly revised estimation policy. The Enron record remains: M1
validates the factorization mechanism; the M4 MPLE joint simulation is a marked
parameter-plug-in sensitivity; neither supplies a converged higher-order MCMLE
dependence estimate.

**Evidence.** Local technical smoke bundle:
`results/models/enron_joint_footprint_mcmle_smoke/`, especially
`candidate_simulation_scores.csv`, `selected_candidates.csv`,
`model_status.csv`, `split_status.csv`, and
`diagnostics/mcar_replicate_001__M1.txt`.

### CAVIAR direction and phase-label gate — static full matrix approved

The UCINET publisher documents directed, valued police-wiretap communication
matrices but does not specify the row-to-column orientation. A peer-reviewed
study using Project Caviar states explicitly that its directed links point from
caller to receiver. The local source record therefore approves the exact
unique-labelled 110-node `CAVIAR_FULL.csv` matrix with **rows as callers/senders
and columns as receivers**.

The approval does not extend to the 11 phase matrices. `CAVIAR7` repeats actor
label `9` at positions 9 and 15 in both the CSV and paired UCINET header. There
is no source-level correction identifying the second position, so it remains
unaltered and is excluded from all directed and temporal inference. We will not
merge, impute, or silently rename the duplicate actor.

**Decision.** CAVIAR is now eligible only as a **static dyadic** benchmark from
the full matrix: arc, footprint, formal-concept, and dyadic-role targets are
allowed; native-event and chronology targets are not. The reproducible build
requires `make phase2-caviar-static-prep`. The supporting source note and
scope-specific gate are `docs/research_caviar_direction_sources.md` and
`data/metadata/gates/caviar_direction.json`.

**Materialization confirmation.** The local CAVIAR static build completed with
the approved full-matrix scope and direction gate. The pinned full matrix has
110 nodes, 295 positive nonloop directed arcs, total communication weight 3,546,
zero nonzero diagonal entries, and binary directed density 2.460384%. The next
gate is the cap-first formal-concept representation audit at `(|T|,|H|) ≤ (3,3)`;
it is a static representation diagnostic, not a claim that aggregate CAVIAR
communication ties encode recorded group events.

**Representation-screening result.** The cap-first `(|T|,|H|) ≤ (3,3)` audit
completed with 80 concepts, 79 involving a multi-actor tail or head, and no
concept with an actor in both roles. The capped concept footprints cover 181 of
295 observed arcs (61.356%), and arc multiplicity is 0 / 1 / 4 / 12 at the
minimum / median / 95th-percentile / maximum. This is adequate to carry the
formal-concept target as a clearly labelled static representation sensitivity.
It is not a native-event result: aggregate wiretap dyads cannot establish that
the concepts were recorded group interactions.

**Pilot contract.** The fixed three-replicate, 30% arc-first MCAR static LP
pilot uses the full 110-node CAVIAR matrix and the same cap pair. It evaluates
directed arc recovery and reports concept-footprint coverage; it cannot evaluate
native-event recovery or chronology.

**Static arc-LP pilot result.** The deterministic three-replicate MCAR pilot
completed on the full 110-node, 295-arc matrix. Each replicate masked 88 arcs
(29.830508% of the graph) and evaluated them against 88 sampled true nonedges.
The best uncalibrated heuristic was total directed Adamic--Adar: mean ROC-AUC
`0.738873` (SD `0.005685`) and mean PR-AUC `0.764533` (SD `0.006538`). The
unweighted total-common-neighbor score gave mean ROC-AUC `0.718879` (SD
`0.003404`) and PR-AUC `0.716096` (SD `0.013305`).

These values are bounded **arc-recovery pilot** results on balanced random
true-nonedge panels. They are not calibrated probabilities, no ERGM has entered
this result, and they do not test native events, temporal forecasting, or the
defective CAVIAR phase series. The formal-concept coverage in the pilot matches
the independent representation audit: 80 formal concepts cover 181 of 295 arcs
(61.356%), with an augmented section of 374 tail/head pairs used only to ensure
arc coverage in the diagnostic.

**Static ERGM ladder feasibility.** All six plan-aligned models—M0, M1, M2, M3,
M4, and M4c—completed maximum pseudolikelihood estimation on the full CAVIAR
network with `fit_succeeded` status and no recorded warnings. This establishes
that the full static graph, its direction convention, and the planned directed
term specifications are computationally compatible under MPLE. It is a
structural feasibility result only: it does not supply held-out predictions,
validate coefficients as MCMC-MLE estimates, establish MCMC mixing, or alter
the restriction against phase-series, native-event, or temporal claims. The
result clears only the static masked conditional-score feasibility check.

**Masked ERGM conditional-score pilot.** All 12 model-by-replicate fits (four
models across the three frozen MCAR masks) succeeded and produced conditional
probabilities. Relative to the M1 mutuality model, the M3 degree-plus-OTP
extension produced a substantial score lift: mean ROC-AUC `0.8590` (SD
`0.0047`), PR-AUC `0.8770` (SD `0.0126`), and log loss `1.3645` (SD `0.0060`),
versus M1's `0.7216`, `0.7164`, and `1.4584`, respectively. It also exceeds the
best uncalibrated arc heuristic (total directed Adamic--Adar: ROC-AUC `0.7389`,
PR-AUC `0.7645`) on this fixed balanced panel. The M3–M1 differences are
`+0.1374` ROC-AUC, `+0.1606` PR-AUC, and `−0.0939` log loss; against total
directed Adamic--Adar, the rank-metric differences are `+0.120127` and
`+0.112467`.

M4c's added OSP/ISP closure and cyclic-triple terms change rank discrimination
only slightly relative to M3 (ROC-AUC `0.8639`, PR-AUC `0.8828`) while worsening
mean log loss to `1.3835` and reducing threshold-0.5 recall and F1. With only
three fixed pilot masks, this is not evidence that M4c is inferior in general;
it does mean that its additional terms do **not** earn a clear incremental
conditional-score benefit in the CAVIAR pilot. The density-only M0 and mutuality
M1 models produce no 0.5-threshold positives, so their threshold precision/MCC
are undefined; their threshold-free AUC and log-loss values remain valid.

**Interpretation.** The supported CAVIAR conclusion is narrow but useful:
under static MCAR arc masking and MPLE, the planned directed structural ERGM
extension improves conditional discrimination and log loss beyond the baseline
and local heuristic pilot. It remains a pseudolikelihood, static-dyadic result,
not MCMC-MLE inference, a group-event result, a temporal forecast, or a result
about the excluded phase series.

### Ciel direction-semantics gate — remains blocked

The official CielNet page and a later published reuse both establish a 25-person
directed, valued wiretap-communication relation, but neither maps the published
matrix rows and columns to caller/initiator and receiver/recipient. The primary
book preview identifies a "Direction of Contact" section, but does not expose
the needed coding pages. General UCINET matrix conventions cannot safely supply
the missing source-specific semantics.

**Decision.** The Ciel gate is explicitly recorded as unapproved in
`data/metadata/gates/ciel_direction.json`. No static directed graph, formal
concept section, LP/HP panel, or ERGM result will be built from Ciel in this
paper without a source that states the orientation. The data remain preserved
for provenance and may be reassessed if the primary Appendix or an authoritative
replication codebook becomes available. Supporting evidence is recorded in
`docs/research_ciel_direction_sources.md`.

**Local integrity audit.** The preserved source audit confirms a 25-node matrix
with 45 positive off-diagonal cells, no nonzero diagonal entries, and no
duplicate labels. Those checks establish that the local matrix is structurally
usable, but they do not resolve its row-to-column communication semantics. No
directed derived data were created.

### Jmail v1 header audit — technically viable, policy gate remains closed

The no-body Jmail audit processed all 1,781,028 structured rows and found every
message ID nonempty and unique. It found 180,572 missing senders (10.139%) and
5,023 invalid or missing timestamps (0.282%). Under the provisional
singleton-sender, distinct-To-plus-Cc rule, 1,120,328 records (62.903%) are
candidate native events; no restricted event file was built.

**Decision.** Unique IDs and recipient arrays make a filtered header-based
native-event view technically feasible. They do not settle admissibility. The
provider combines House Oversight, DOJ, and Yahoo/DDoSecrets provenance streams;
the gate therefore remains unapproved pending source-stream inclusion/release
policy, inspection of the full recipient-malformation audit, entity-resolution
scope, missing-sender handling, and final To/Cc/Bcc policy. The explicit block
is `data/metadata/gates/jmail_v1_admissibility.json`; the provenance assessment
is `docs/research_jmail_admissibility_sources.md`.

### MathOverflow reconstruction profile — 30-day primary recommended

The audit found 341,167 posts, no invalid timestamps, and no answer lacking a
parent ID. It retained 148,432 eligible question askers, while excluding 4,461
ownerless questions (2.918%) and 2,881 ownerless answers (1.542%). It also
identified 7,773 self-answers and 3,111 duplicate eligible answers, leaving
168,004 distinct eligible question-answerer pairs after duplicate collapse.

Response latency is strongly right-skewed: the first distinct-answerer latency
has median 0.317 days, 75th percentile 2.355 days, 90th percentile 216.407
days, and 95th percentile 985.838 days. A 30-day window retains 142,958 pairs
(85.092%) and 91,161 questions with one or more answerer (96.172% of the
365-day descriptive count). It adds useful short-to-medium response coverage
beyond 7 days without treating years-late answers as part of the same group.

**Recommendation, pending approval.** Use 30 days as the primary reconstructed
event window, use 7 and 90 days as bounded sensitivities, leave 365 days
descriptive only, exclude comments, anonymous users, and self-answers, collapse
duplicate answerers per question, and retain only rows present in the public
dump. The policy remains unapproved in
`data/metadata/gates/mathoverflow_reconstruction_policy.json`; creating native
events therefore remains blocked.
