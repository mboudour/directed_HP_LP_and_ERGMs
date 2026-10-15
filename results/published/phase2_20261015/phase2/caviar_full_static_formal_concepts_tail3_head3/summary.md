# Capped directed formal-concept audit

- Dataset: `caviar_full_static`
- Fixed node universe: `110` nodes
- Observed binary directed arcs: `295`
- Cap-first enumeration: `|T| ≤ 3`, `|H| ≤ 3`
- Concepts emitted: `80`
- Concepts with tail or head arity greater than one: `79`
- Concepts with a node in both roles: `0`
- Observed arcs covered by capped concept footprints: `181/295` (`61.356%`)
- Arc concept multiplicity (min / median / p95 / max): `0 / 1 / 4.00 / 12`

The cap is applied during enumeration rather than to an already enumerated concept set. This output is a required representation diagnostic before choosing analysis caps and running missingness experiments. It does not assert that formal concepts are recorded group events.
