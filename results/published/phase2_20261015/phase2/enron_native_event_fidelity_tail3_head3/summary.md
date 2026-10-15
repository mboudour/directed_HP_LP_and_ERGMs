# Native-event and formal-concept fidelity audit

- Dataset: `enron_20150507`
- Fixed node universe: `100`
- Static directed arcs: `635`
- Caps: `|T| <= 3`, `|H| <= 3`
- Cap-eligible recorded event records: `7,793`
- Cap-eligible recorded event types: `719`
- Formal concepts: `232`

## Exact role equality

- Matching tail/head pairs: `0`
- Formal-concept precision against recorded event types: `0.000000`
- Recorded event-type recall by formal concepts: `0.000000`

## Footprint agreement

- Native-event cap footprint arcs: `628`
- Formal-concept footprint arcs: `551`
- Footprint Jaccard: `0.856693`
- Native footprint covered by concepts: `0.866242`
- Concept footprint covered by native events: `0.987296`

## Cover diagnostics

- Concepts without an exact recorded-event type: `232`
- Concepts with at least two contributing recorded event types: `232`
- Event types with two or more strictly contained concept footprints: `0`
- Best event-to-concept role-distortion cases: `36`

This is a representation-fidelity diagnostic. It does not assert that formal concepts are observed email groups or that native events can be reconstructed from the aggregate directed graph.
