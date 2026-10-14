# Enron MCMLE feasibility core

## Decision

The primary strict Enron core-100 is retained for the paper’s main static
missingness, heuristic, MPLE, formal-concept, and native-event analyses.

On the frozen `mcar_replicate_001` projection, M1 MCMLE was a valid
factorization diagnostic, but M2 stopped with **unconstrained MCMC sampling did
not mix at all** and M4 did not converge within an interactive-scale run. The
researcher approved a deterministic, nested **core-50** only for MCMLE
feasibility and conditional-joint-score sensitivity work.

## Fixed selection rule

The core-50 is exactly the rows with `rank = 1, …, 50` from the already
materialized strict primary `custodian_core100_nodes.csv`. Thus it is:

- selected by the original top-100 sent-plus-received-activity rule;
- a strict nested subset, with no reranking, fit-based selection, or tuning;
- based on the same approved 1998–2002 timestamp interval, strict address map,
  full-event participant rule, and message-copy policy as the primary data.

The builder filters recorded events to those whose sender and **every** recipient
belong to that fixed core, then derives its static and calendar-month arc tables.

## Scope and non-substitution rule

This core is **not** a replacement primary benchmark and cannot be used to
silently replace any core-100 result. Its outputs are limited to:

1. MCMC-MLE feasibility diagnostics;
2. non-degeneracy and convergence checks; and
3. conditional joint-footprint (`L2`/`L3-F`) sensitivity calculations, if the
   model passes those checks.

All reporting must say `nested Enron core-50 MCMLE feasibility sensitivity`.
A successful fit there does not erase the recorded core-100 M2/M4 MCMC failures.

## Materialization

```zsh
make phase2-enron-mcmle-core50
```

To prepare six isolated event-first splits, their heuristic and hard-negative
panels, and the fixed joint-score input bundle, run:

```zsh
make phase2-enron-mcmle-core50-inputs
```

All resulting paths include `enron_mcmle_core50`; they never overwrite the
primary core-100 mask or score bundles.

## First MCMC-MLE gate

Before fitting any MCMC-MLE model, audit the available candidate footprints:

```zsh
make phase2-enron-mcmle-core50-candidates
```

It reports only aggregate candidate counts. In particular, it distinguishes
the exact-two-unknown-dyad rule from the stricter requirement that every
unknown arc has an observed reverse. The M2 target is launched only after this
audit identifies a nonempty, predeclared candidate class.

The completed core-50 audit found no strict candidate in
`mcar_replicate_001`, but found five in `mcar_replicate_002`. The M2 target
therefore uses **the earliest MCAR replicate with a nonempty strict class**:
`mcar_replicate_002`. This is a data-availability rule applied before any M2
fit or score is inspected; it preserves the original exactly-two-unknown-dyad
and observed-reverse-arc design without relaxing it.

The first computational gate is then M2 (edges, mutuality, geometrically
weighted in-degree, and geometrically weighted out-degree) on
`mcar_replicate_002`:

```zsh
make phase2-enron-mcmle-core50-m2-gate
```

The target uses the repository’s cross-platform bounded-command runner with a
120-second hard wall-clock limit. It selects only candidates with exactly two
unknown footprint dyads and observed reverse arcs, fits no other model, and
writes its raw execution log separately from the model output directory. A
timeout, explicit nonmixing error, or any non-convergence diagnostic is a gate
failure and must be recorded before deciding whether M3 or M4 is attempted.

The builder writes ignored local data to:

```text
data/processed/enron_20150507/custodian_mcmle_core50_nodes.csv
data/processed/enron_20150507/custodian_mcmle_core50_native_events.parquet
data/processed/enron_20150507/custodian_mcmle_core50_static_arcs.parquet
data/processed/enron_20150507/custodian_mcmle_core50_monthly_arcs.parquet
data/metadata/enron_20150507_mcmle_core50.json
docs/data_audits/enron_20150507_mcmle_core50.md
```
