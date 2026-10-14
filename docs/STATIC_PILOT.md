# Static Phase 2 pilot

`scripts/30_run_static_benchmark.py` is the single local driver for the plan's
**bounded static pilot**. It operates only on a prepared and eligible static directed
arc table; it does not parse raw data or bypass any source-specific gate.

## What it creates

For each selected prepared dataset, the driver writes a new local bundle under
`results/phase2/<dataset>_static_pilot/` (or an explicit `--output-dir`):

- frozen loop-free static edge and node inputs;
- the bounded formal-concept section, augmented section, and representation-fidelity
  coverage diagnostic;
- deterministic arc-first MCAR or MNAR-out masks;
- OI/two-path, OO/shared-target, II/shared-source, summed, and directed
  Adamic--Adar scores;
- random true-nonedge candidate panels and ROC-AUC/PR-AUC results for each replicate;
- `r_inputs/static_edges.csv` and `r_inputs/nodes.csv`, consumed directly by
  `r/models/static_directed_ergm_ladder.R`.

The bundle is local and ignored by Git. It is reproducible from the named prepared
inputs, seed, mask rate, and concept caps saved in `run_manifest.json`.

## Scope boundary

This is **not the final paper experiment**. In particular, the pilot does not yet claim
hyperlink prediction results, ERGM score lifts, calibrated probabilities/log loss,
conditional simulation, NHP-D results, event-first masking, or target-specific hard
negative panels. Its purpose is to make the first pilot-gate evidence inspectable before
those more expensive analyses are enabled.

## Example

After the EU-core preparation audit has completed, the standard bounded pilot is:

```zsh
make phase2-static ARGS="--dataset eu_core --mechanism mcar --replicates 3 --mask-rate 0.30 --tail-cap 2 --head-cap 2"
```

It will refuse to overwrite an existing output bundle. Pass an explicit new
`--output-dir` for a new configuration; use `--overwrite` only for an intentionally
repeated, already archived configuration.

For a static ERGM ladder on the bundle that this command creates:

```zsh
Rscript r/models/static_directed_ergm_ladder.R \
  --input=results/phase2/eu_core_static_pilot/r_inputs/static_edges.csv \
  --nodes=results/phase2/eu_core_static_pilot/r_inputs/nodes.csv \
  --output-dir=results/models/eu_core_static_ladder \
  --estimate=MPLE
```

The R driver produces all specified models (`M0` through `M4c`), but records individual
model failures visibly in `model_status.csv`; it never silently changes the specification.
