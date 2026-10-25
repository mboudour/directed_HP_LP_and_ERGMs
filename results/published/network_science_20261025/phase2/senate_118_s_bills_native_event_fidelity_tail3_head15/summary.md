# Native-event and formal-concept fidelity audit

- Dataset: `senate_118_s_bills`
- Fixed node universe: `105`
- Static directed arcs: `5,619`
- Caps: `|T| <= 3`, `|H| <= 15`
- Cap-eligible recorded event records: `4,145`
- Cap-eligible recorded event types: `3,398`
- Formal concepts: `474`

## Exact role equality

- Matching tail/head pairs: `0`
- Formal-concept precision against recorded event types: `0.000000`
- Recorded event-type recall by formal concepts: `0.000000`

## Footprint agreement

- Native-event cap footprint arcs: `4,713`
- Formal-concept footprint arcs: `3,695`
- Footprint Jaccard: `0.609803`
- Native footprint covered by concepts: `0.675790`
- Concept footprint covered by native events: `0.861976`

## Cover diagnostics

- Concepts without an exact recorded-event type: `474`
- Concepts with at least two contributing recorded event types: `474`
- Event types with two or more strictly contained concept footprints: `0`
- Best event-to-concept role-distortion cases: `156`

This is a representation-fidelity diagnostic. It does not assert that formal concepts are observed email groups or that native events can be reconstructed from the aggregate directed graph.
