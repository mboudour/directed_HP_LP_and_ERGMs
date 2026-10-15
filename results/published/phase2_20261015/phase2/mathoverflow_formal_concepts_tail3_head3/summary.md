# Capped directed formal-concept audit

- Dataset: `mathoverflow_stackexchange_2024`
- Fixed node universe: `100` nodes
- Observed binary directed arcs: `1,020`
- Cap-first enumeration: `|T| ≤ 3`, `|H| ≤ 3`
- Concepts emitted: `207`
- Concepts with tail or head arity greater than one: `207`
- Concepts with a node in both roles: `0`
- Observed arcs covered by capped concept footprints: `676/1,020` (`66.275%`)
- Arc concept multiplicity (min / median / p95 / max): `0 / 1.0 / 5.00 / 11`

The cap is applied during enumeration rather than to an already enumerated concept set. This output is a required representation diagnostic before choosing analysis caps and running missingness experiments. It does not assert that formal concepts are recorded group events.
