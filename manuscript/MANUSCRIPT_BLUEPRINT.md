# Paper 1 manuscript blueprint and evidence map

**Working title:** *ERGM Benchmark for Directed Link and Hyperlink Prediction under Missingness*

**Phase:** 3 — evidence-first manuscript construction
**Last updated:** 2026-10-15
**Status:** blueprint only; no journal template or submission format selected

## 1. Paper identity

This paper studies the relationship between directed link prediction (LP),
directed hyperlink prediction (HP), and ERGM-derived scores when observations
are missing. Its central contribution is not a forecasting comparison. Instead,
it separates three targets that are often conflated after an interaction record
has been aggregated into a directed graph:

1. **Dyadic footprints:** directed arcs induced by interaction records.
2. **Formal concepts:** cap-first, algebraically derived directed groups from a
   binary aggregate relation.
3. **Native events:** recorded ordered tail/head group interactions.

The primary benchmark uses static missingness. The chronological Enron/EU-core
analysis is a deliberately bounded diagnostic of the history-versus-
contemporaneous-score distinction; it is not a forecasting study.

## 2. Non-negotiable evidence boundaries

All manuscript text, tables, captions, and conclusions must respect these
constraints.

| Topic | Admissible wording | Prohibited or unsupported wording |
|---|---|---|
| ERGM fits | MPLE-based **conditional-score** or factorized conditional-pseudolikelihood footprint rankings | Joint ERGM probabilities, MCMC-MLE inference, or general ERGM goodness-of-fit where no successful MCMC gate exists |
| Footprint scores | `L1`, `L1g`, and factorized `L2` are distinct score constructions with the stated conditioning | Calling the factorized `L2` the matched-marginal score or a simulated joint footprint probability |
| Formal concepts | Derived structural targets; evaluate representation and concept recovery separately | Recovered email events, observed groups, or a one-to-one event representation |
| Paired uncertainty | Within-fixed-network, matched-mask uncertainty only | Population inference, cross-network pooling, or independent-network replication |
| Missingness | Exact event-type MCAR and planned oracle MNAR-out mechanisms; realised type/record/arc rates reported separately | Treating nominal type masking as a common severity measure across mechanisms |
| Chronological analysis | Bounded history-versus-contemporaneous diagnostic | Forecasting accuracy claim, rolling-origin evaluation, or a STERGM/RHEM comparison |
| Neural baseline | Explicit reproduction-gate exclusion | Any neural benchmark result or performance comparison |

The authoritative scope record is `docs/PHASE2_COMPLETION_REVIEW.md`; detailed
results and interpretation limits are in `docs/PHASE2_FINDINGS.md`.

## 3. Core research questions and admissible answers

| Research question | Admissible answer based on Phase 2 | Evidence location |
|---|---|---|
| RQ1. What target is being recovered after directed interactions are aggregated? | Footprints, formal concepts, and native events are empirically distinct targets and must be evaluated separately. | Enron and MathOverflow fidelity audits; Enron rewiring null |
| RQ2. Do directed ERGM conditional scores improve random-panel native-event footprint ranking under missingness? | In the frozen-mask primary benchmark, `M4c::L1g` improves PR-AUC over predeclared `M0::L1` within both datasets and both primary mechanisms. | Paired ERGM uncertainty bundles |
| RQ3. Does strong footprint ranking recover roles within a native event? | No general role-recovery conclusion follows: random-panel lifts do not transfer consistently to reversal or role-exchange panels. | Native hard panels and role-assignment branches |
| RQ4. Do formal concepts recover native group events? | No. Exact tail/head matches are zero in the audited Enron and MathOverflow cores despite substantial footprint overlap. | Native-event/formal-concept fidelity audits |
| RQ5. What does temporal dependence add? | The paper documents only a bounded history-versus-contemporaneous diagnostic for Enron/EU-core; it does not estimate a full forecasting gain. | Temporal model bundles and Phase 2 findings |

## 4. Section architecture

### 4.1 Abstract (about 175–220 words)

Must include:

- The missingness-centred question and the target ladder.
- The two primary native-event datasets: strict Enron custodian core and
  reconstructed MathOverflow core.
- Event-first 30-mask MCAR and MNAR-out design, random and hard panels.
- The central conditional-score result, carefully qualified as a matched-mask
  performance comparison.
- The formal-concept/non-event result.
- The limits: no MCMC-derived higher-order joint result, no neural result, and
  no forecasting claim.

Avoid coefficient claims, generic “better prediction” language, and a claim
that the paper estimates real-world message probabilities.

### 4.2 Introduction

1. Motivate prediction from incomplete directed interaction data and connect to
   the project’s earlier missingness work.
2. Identify the unresolved conflation: an aggregate directed graph retains
   dyadic footprints but not necessarily ordered group-event identities.
3. State the target ladder and why a directed HP benchmark needs target-specific
   panels.
4. Introduce ERGM conditional scores as a structured comparator to local
   directed-LP scores, not as an automatic joint event model.
5. State contributions and delimit Paper 1 from the future temporal forecasting
   paper.

### 4.3 Targets and score decomposition

Define directed graph notation, native tail/head events, induced footprints, and
cap-first formal concepts. Present the target ladder before any score metric.

Then distinguish:

- single-arc conditional score;
- footprint summaries `L1` and `L1g`;
- factorized conditional-pseudolikelihood `L2`;
- a matched-observation joint construction, discussed conceptually but not
  claimed as a successful Enron higher-order MCMC result;
- history-only versus contemporaneous terms in the bounded temporal check.

The formal-concept/non-identifiability argument must precede empirical results,
so that the zero exact-match finding is a test of a stated distinction rather
than a post hoc explanation.

### 4.4 Data and benchmark design

Cover provenance, privacy boundaries, and target eligibility.

- **Enron:** strict 1998–2002, 110 approved custodian identities; primary
  core-100 has 7,820 retained complete events and 635 static arcs. Describe the
  conservative internal-custodian selection boundary.
- **MathOverflow:** reconstructed native interaction target on its approved
  core; document reconstruction policy and avoid calling the records emails.
- **EU-core:** directed temporal dyadic diagnostic; no native-event primary
  claim.
- **CAVIAR:** full static directed dyadic/footprint-only analysis; phase
  matrices excluded from general results.
- **Ciel and Jmail:** not analysed as substantive results; report gates only.

For native events, state that a sampled unit is an ordered tail/head **event
type**, with duplicate records of the selected type withheld together. Explain
why type, record, and projection-arc loss are all reported.

### 4.5 Models, panels, metrics, and uncertainty

- Directed LP features and lifted footprint aggregation.
- Static ERGM ladder and MPLE conditional scoring.
- `L1`, `L1g`, and factorized `L2` definitions and limitations.
- Random arity-matched native-event panels.
- Directed hard panels: reversal/orientation and role exchange.
- Fixed-role assignment task.
- Ranking-only metrics for uncalibrated scores.
- 30 frozen masks per primary mechanism/data set; whole-mask percentile
  bootstrap (10,000 draws) and paired sign-flip test (20,000 draws).

Explain that the paired analysis treats masks as repeated missingness
realizations for the same fixed network, not as independent networks.

### 4.6 Results

Organize in the following sequence:

1. **Eligibility and target distinction.** Data scope table, cap-first sections,
   and formal-concept/native-event fidelity.
2. **Primary native-event random panels.** Heuristic and ERGM footprint
   comparisons on Enron and MathOverflow, MCAR and MNAR-out.
3. **Hard panels and role assignment.** Show why random-panel footprint
   performance does not imply directional group-role recovery.
4. **ERGM paired contrasts.** Present predeclared M0-to-M4c random-panel
   comparison with within-dataset uncertainty.
5. **Bounded chronological check.** Present only the diagnostic result and
   explicitly close the forecasting boundary.
6. **Supplementary sensitivity and gates.** Point readers to supplemental
   material for Regime C, MNAR-in/rate grid, rewiring null, and feasibility
   records.

### 4.7 Discussion

The discussion should make four claims only:

1. Target choice is a central identification decision in directed HP.
2. Conditional ERGM footprint scores provide material random-panel ranking
   gains over the density baseline on these frozen missingness benchmarks.
3. Strong footprint overlap or random-panel performance cannot be equated with
   recovering a recorded directed group event or its roles.
4. Full temporal forecasting, STERGM/RHEM competition, and successful
   higher-order joint MCMC estimation remain separate work.

Explicitly discuss the strict Enron selection policy, reconstructed
MathOverflow events, the cap, fixed 100-node cores, case-control panels,
oracle MNAR design, and lack of cross-network inferential pooling.

## 5. Main table specifications

All tables must be generated from tracked aggregate-only data. No raw emails,
addresses, event identifiers, candidate-level predictions, or actor maps may be
introduced into manuscript outputs.

| Table | Purpose | Primary inputs | Required notes |
|---|---|---|---|
| 1. Data and target eligibility | State the admissible scope before results | `configs/datasets.yaml`, `docs/PHASE2_COMPLETION_REVIEW.md`, aggregate audits | Separate native-event, dyadic temporal, static-only, and blocked/pending cases |
| 2. Target-fidelity diagnostics | Show concepts are not recovered events | `phase2/*_native_event_fidelity_tail3_head3/summary.json`; Enron rewiring aggregate | Exact matches, precision/recall, footprint overlap, and scope qualifier |
| 3. Native-event benchmark performance | Primary 30-mask random and hard-panel results | Native heuristic, hard-panel, role-assignment, and ERGM aggregate metric summaries | Split results by dataset, mechanism, target/panel, and score family; do not use one overall winner |
| 4. Predeclared paired ERGM contrasts | Quantify M4c/L1g versus M0/L1 random-panel PR-AUC lift | `models/*_native_ergm_paired_uncertainty/paired_differences.csv` | Mean difference, 95% percentile interval, 20,000-draw sign-flip p value; within-dataset only |
| 5. Bounded chronological diagnostic | Prevent expansion into forecasting | Enron/EU-core temporal aggregate model outputs | Label MPLE/history/contemporaneous terms and state no forecast claim |
| 6. Gate and exclusion record | Make non-admissible branches transparent | Phase 2 completion review and NHP-D gate | Suitable for main-text compact table or supplement, depending on journal space |

## 6. Main figure specifications

| Figure | Message | Construction rule |
|---|---|---|
| 1. Target ladder and score map | Native events, footprints, and concepts are different targets; map LP and ERGM scores to each | Original schematic; no empirical microdata |
| 2. Formal concepts versus native events | High footprint overlap can coexist with zero exact role matches | Aggregate fidelity values and optional degree-preserving-null distribution only |
| 3. Primary benchmark contrasts | Random-panel ERGM/heuristic performance versus hard-panel/role results | Dataset-mechanism faceting; preserve separate target panels and uncertainty meaning |
| 4. Paired random-panel ERGM lift | Predeclared `M4c::L1g − M0::L1` PR-AUC differences | Four rows: Enron/MathOverflow × MCAR/MNAR-out; show bootstrap intervals only |
| 5. Bounded temporal score logic | History-only versus contemporaneous conditional-score distinction | Conceptual/aggregate diagnostic; no forecasting horizon or forecast-error graphic |

## 7. Known primary numerical anchors

These values are admissible only with the stated scope and will be generated
from source tables rather than manually retyped in the manuscript.

| Dataset | Mechanism | Contrast | Mean PR-AUC difference | 95% percentile bootstrap CI | Paired sign-flip p value |
|---|---|---|---:|---|---:|
| Enron | MCAR | `M4c::L1g − M0::L1` | +0.3584 | +0.3519 to +0.3648 | 0.00005 lower-bound resolution |
| Enron | MNAR-out | `M4c::L1g − M0::L1` | +0.3324 | +0.3269 to +0.3379 | 0.00005 lower-bound resolution |
| MathOverflow | MCAR | `M4c::L1g − M0::L1` | +0.2396 | +0.2305 to +0.2485 | 0.00005 lower-bound resolution |
| MathOverflow | MNAR-out | `M4c::L1g − M0::L1` | +0.2394 | +0.2303 to +0.2484 | 0.00005 lower-bound resolution |

The p-value text must say that the Monte Carlo lower resolution is
`1 / 20,001`, rather than report zero.

## 8. Supplement plan

Supplementary material should contain:

- full score-by-panel tables and all score definitions;
- realised mask severities and removal strata;
- all cap-first arity distributions;
- Regime C footprint-free concept stress results;
- rate and MNAR-in sensitivity grid;
- Enron degree-preserving rewiring null;
- M4 MPLE parameter-plug-in joint-footprint sensitivity, clearly labelled;
- MCMC feasibility records and NHP-D reproduction gate;
- source/data provenance and privacy-preservation details.

## 9. Explicit exclusions from Paper 1

Do not revive these as unreported primary analyses:

- Enron MCMC-derived `L3-F` or `L3-C` higher-order ERGM results;
- neural NHP-D results;
- Regime K;
- combined masking-and-forecasting analyses;
- full rolling-origin forecasting;
- STERGM, RHEM, or any claim about formation/dissolution forecasting;
- Ciel directional results; and
- Jmail substantive results before its source, entity, and recipient policy
  gates have passed.

These exclusions are methodological findings and scope controls, not missing
appendices to be silently filled later.

## 10. Reproducible Phase 3 build order

1. Build tracked scripts that extract aggregate table inputs from the published
   Phase 2 bundle.
2. Render main tables and figure-ready aggregate CSVs into `manuscript/tables/`
   and `manuscript/figures/` without exposing sensitive data.
3. Draft methods and results against those generated artifacts.
4. Draft introduction/discussion to match the permitted claim language.
5. Select a journal/template before creating the submission-formatted source
   (LaTeX, Word, or another journal-specific format).

Until a target journal is selected, Markdown is the canonical manuscript source
and no journal-specific styling decision is implied.
