# Native-event and formal-concept fidelity audit

- Dataset: `mathoverflow_stackexchange_2024`
- Fixed node universe: `100`
- Static directed arcs: `1,020`
- Caps: `|T| <= 3`, `|H| <= 3`
- Cap-eligible recorded event records: `1,946`
- Cap-eligible recorded event types: `1,071`
- Formal concepts: `207`

## Exact role equality

- Matching tail/head pairs: `0`
- Formal-concept precision against recorded event types: `0.000000`
- Recorded event-type recall by formal concepts: `0.000000`

## Footprint agreement

- Native-event cap footprint arcs: `1,014`
- Formal-concept footprint arcs: `676`
- Footprint Jaccard: `0.663386`
- Native footprint covered by concepts: `0.664694`
- Concept footprint covered by native events: `0.997041`

## Cover diagnostics

- Concepts without an exact recorded-event type: `207`
- Concepts with at least two contributing recorded event types: `207`
- Event types with two or more strictly contained concept footprints: `0`
- Best event-to-concept role-distortion cases: `19`

This is a representation-fidelity diagnostic. It does not assert that formal concepts are observed email groups or that native events can be reconstructed from the aggregate directed graph.
