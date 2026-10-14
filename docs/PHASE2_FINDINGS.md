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

**Boundary.** This resolves the timestamp-only gate. It does not approve the custodian-address map, a message-copy/retransmission policy, or the treatment of events containing an unmapped participant. Those remain independent preconditions for the primary custodian-node projection.

**Evidence.** Versioned policy: `configs/enron_temporal_policy.yaml`; locally generated profile: `data/metadata/enron_20150507_event_timestamp_profile.json`, `data/metadata/enron_20150507_event_timestamp_year_counts.csv`, and `docs/data_audits/enron_20150507_event_timestamp_profile.md`.
