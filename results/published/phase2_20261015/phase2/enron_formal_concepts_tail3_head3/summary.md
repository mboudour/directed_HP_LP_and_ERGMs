# Capped directed formal-concept audit

- Dataset: `enron_20150507`
- Fixed node universe: `100` nodes
- Observed binary directed arcs: `635`
- Cap-first enumeration: `|T| ≤ 3`, `|H| ≤ 3`
- Concepts emitted: `232`
- Concepts with tail or head arity greater than one: `232`
- Concepts with a node in both roles: `0`
- Observed arcs covered by capped concept footprints: `551/635` (`86.772%`)
- Arc concept multiplicity (min / median / p95 / max): `0 / 2 / 5.00 / 10`

The cap is applied during enumeration rather than to an already enumerated concept set. This output is a required representation diagnostic before choosing analysis caps and running missingness experiments. It does not assert that formal concepts are recorded group events.
