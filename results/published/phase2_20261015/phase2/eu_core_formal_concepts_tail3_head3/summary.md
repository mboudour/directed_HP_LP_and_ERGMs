# Capped directed formal-concept audit

- Dataset: `email_eu_core_temporal`
- Fixed node universe: `100` nodes
- Observed binary directed arcs: `2,682`
- Cap-first enumeration: `|T| ≤ 3`, `|H| ≤ 3`
- Concepts emitted: `45`
- Concepts with tail or head arity greater than one: `45`
- Concepts with a node in both roles: `0`
- Observed arcs covered by capped concept footprints: `225/2,682` (`8.389%`)
- Arc concept multiplicity (min / median / p95 / max): `0 / 0.0 / 1.00 / 5`

The cap is applied during enumeration rather than to an already enumerated concept set. This output is a required representation diagnostic before choosing analysis caps and running missingness experiments. It does not assert that formal concepts are recorded group events.
