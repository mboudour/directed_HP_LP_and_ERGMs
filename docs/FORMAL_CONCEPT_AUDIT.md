# Capped directed formal-concept audit

This local-only audit implements the representation gate in Sections 2, 6.1, and 9.5 of the agreed plan. It enumerates the formal-concept section of a prepared directed graph, with both tail and head caps applied **during** enumeration. It reports the consequences of that cap instead of treating a capped section as the full set of observed group events.

## EU-core screening audit

After the EU-core source preparation has completed, run:

```zsh
make phase2-eu-core-concepts
```

This fixed screening target uses the already selected core-100 node universe and the cap pair `(|T| ≤ 3, |H| ≤ 3)`. It deliberately does not infer native events from same-sender/same-timestamp rows. It overwrites only files belonging to this deterministic result bundle:

```text
results/phase2/eu_core_formal_concepts_tail3_head3/
```

## Output contract

- `concepts.csv` contains canonical tail/head sets as JSON arrays, their role arities, footprint size, and role-overlap count.
- `arity_distribution.csv` counts concepts by `(tail_arity, head_arity)`.
- `arc_multiplicity.csv` gives every observed directed core arc the number of emitted concept footprints containing it. Zero is a valid result under a cap and is reported rather than concealed.
- `summary.json` and `summary.md` preserve input checksums, fixed node universe, caps, coverage, concept count, role overlap, and multiplicity distribution.

The cap-3 run is a **screening audit**, not the final cap selection. The paper's final caps remain a predeclared decision informed by representation diagnostics and the stated sensitivity values. An attempt to enumerate a larger cap under the default candidate budget fails explicitly before partial work is returned. A larger computation must use an explicit budget and documented pilot decision.

No output here is an HP score, a native-event reconstruction, or a final concept-recovery result. It is evidence for deciding whether the selected representation has sufficient nontrivial concepts and manageable overlap before missingness experiments are scaled.
