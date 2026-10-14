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
