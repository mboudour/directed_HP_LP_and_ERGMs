# Phase 2 automation and data-locality protocol

## Purpose

This document records the repository-first workflow for the agreed paper plan,
*Exponential Random Graph Models as a Statistical Benchmark for Directed Link and
Hyperlink Prediction*.

The repository contains reproducible source code, configuration, tests, aggregate audits,
and provenance documentation. It does **not** contain source archives, raw messages,
address-bearing tables, or generated event/arc tables. Those remain on the researcher's
computer under `data/` and are regenerated locally.

## One-command principle

The project moves away from manual copy-paste execution of individual drivers.
Dataset scripts remain independently runnable for auditability, but the normal local
workflow is:

```zsh
git pull --ff-only
uv sync --extra dev
make phase2-status
```

Once source files have been placed under the paths in `configs/datasets.yaml`, a dataset
runner or Make target performs its deterministic preparation steps. Each driver fails
rather than overwriting an existing artifact. The status command identifies what is ready,
conditional, blocked, missing, or already built.

## GitHub versus local outputs

| Artifact | GitHub | Local computer |
|---|---|---|
| Python/R source, tests, configuration | Yes | Pulled from GitHub |
| Aggregate summaries and privacy-safe audits | Yes | Recreated and committed after review |
| Source archives and raw records | No | Stored under `data/external/` or `data/raw/` |
| Address-bearing or record-level Parquet/CSV | No | Stored under `data/interim/` or `data/processed/` |
| Model objects, large simulation draws and figures | No by default | Stored under `results/` |

Thus the final local step is not a large data download from GitHub. It is a versioned
`git pull` followed by locally reproducible builds from the locally held source data. This
preserves reproducibility while avoiding redistribution of sensitive or bulky material.

## Dataset eligibility and hard gates

The processing registry records each source's current status.

| Dataset | Planned role | Automated preparation | Analysis gate |
|---|---|---|---|
| Enron | Main native-event dataset | Header audit, address-level provenance events, strict custodian mapping, core-100, and calendar-month panels | Run the approved strict projection and inspect its retained-event/core-size evidence |
| EU-core | Main dyadic temporal dataset | Row audit, static graph, core-100, 30-day and sensitivity panels | No native-event target in the main analysis |
| CAVIAR | Main dyadic covert dataset | Matrix integrity and dichotomization preparation | Direction must be verified as caller → receiver; duplicate actor labels must be resolved |
| Ciel | Conditional dyadic covert dataset | Matrix integrity and dichotomization preparation | Relation semantics and direction must be verified |
| Jmail v1 | Conditional native-event dataset | Schema, identifier, timestamp, and recipient-array audit | Provenance, entity resolution, licensing, and derived-release decision |
| MathOverflow | Conditional reconstructed-event dataset | Streaming post audit and question-answer reconstruction preview | Answer-window and record-treatment policy must be fixed |

The code records a failed or pending gate as a result. It never treats a pending dataset as
eligible for a target merely because an input file exists.

## Core and panels

Section 8.3 of the agreed plan specifies the default rule for large graphs: **core-100 is
the top 100 actors ranked by sent plus received activity**, with deterministic lexical
tie-breaking. The Enron plan also specifies the custodian-mailbox node set. The researcher
approved the strict map rule on 2026-10-14: retain only unique rank-one sent-folder
candidate addresses with at least 90% support and no cross-custodian collision; exclude an
entire message if any `To`/`Cc` participant is not in that approved map. The address-level
Enron events remain an auditable provenance layer. The previously created reciprocal-
activity profile remains a robustness diagnostic; it does not replace the primary core-100
rule.

The Enron projection gate also records an explicit **quoted-copy/retransmission policy**.
The current executable implementation supports retaining distinct maildir files after the
completed raw-SHA and Message-ID duplicate audits; selecting a different policy requires
an auditable deduplication implementation before projection.

Temporal panels follow the plan:

- Enron: calendar months after the approved inclusive UTC period from `1998-01-01` through
  `2002-12-31`;
- EU-core: 30-day windows anchored at the first timestamp, with 14- and 28-day
  sensitivity windows;
- CAVIAR: 11 ordered phases, descriptive only after direction validation;
- Ciel: static only;
- Jmail and MathOverflow: no temporal module in this paper.

## Boundaries of automation

The pipeline can automate preprocessing, audits, core construction, concept-enumeration
inputs, masks, and model-input exports. It must **not** decide scientific questions that
the plan leaves conditional. In particular, no final model scaling occurs until the plan's
six pilot gates are passed: data/provenance, representation, ERGM diagnostics, NHP-D
reproduction, scope, and the bounded chronological check.
