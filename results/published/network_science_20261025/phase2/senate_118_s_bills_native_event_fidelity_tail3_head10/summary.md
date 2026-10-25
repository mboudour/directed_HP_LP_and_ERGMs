# Native-event and formal-concept fidelity audit

- Dataset: `senate_118_s_bills`
- Fixed node universe: `105`
- Static directed arcs: `5,619`
- Caps: `|T| <= 3`, `|H| <= 10`
- Cap-eligible recorded event records: `3,956`
- Cap-eligible recorded event types: `3,209`
- Formal concepts: `16`

## Exact role equality

- Matching tail/head pairs: `0`
- Formal-concept precision against recorded event types: `0.000000`
- Recorded event-type recall by formal concepts: `0.000000`

## Footprint agreement

- Native-event cap footprint arcs: `4,290`
- Formal-concept footprint arcs: `251`
- Footprint Jaccard: `0.047762`
- Native footprint covered by concepts: `0.048252`
- Concept footprint covered by native events: `0.824701`

## Cover diagnostics

- Concepts without an exact recorded-event type: `16`
- Concepts with at least two contributing recorded event types: `16`
- Event types with two or more strictly contained concept footprints: `0`
- Best event-to-concept role-distortion cases: `350`

This is a representation-fidelity diagnostic. It does not assert that formal concepts are observed email groups or that native events can be reconstructed from the aggregate directed graph.
