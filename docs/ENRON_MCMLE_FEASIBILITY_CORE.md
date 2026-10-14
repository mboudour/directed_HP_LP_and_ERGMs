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

The builder writes ignored local data to:

```text
data/processed/enron_20150507/custodian_mcmle_core50_nodes.csv
data/processed/enron_20150507/custodian_mcmle_core50_native_events.parquet
data/processed/enron_20150507/custodian_mcmle_core50_static_arcs.parquet
data/processed/enron_20150507/custodian_mcmle_core50_monthly_arcs.parquet
data/metadata/enron_20150507_mcmle_core50.json
docs/data_audits/enron_20150507_mcmle_core50.md
```
