# Revision computations (November 2026)

This folder holds the computations for the revised Network Science manuscript:
the 118th Senate primary benchmark, replications in the 116th and 117th Senates
and the 118th House, and the new analyses requested in review. It is a
self-contained Python re-implementation of the event-first benchmark, plus R
scripts for likelihood-based ERGM estimation and goodness of fit.

The re-implementation reproduces the published 118th Senate outputs in
`results/published/network_science_20261025/`:

- record accounting (4,374 nonempty-head bills, 105 actors, 3,209 cap-eligible types)
- all 60 frozen masks (same seeds and type order)
- the random-negative and sponsor-substitution draws
- the formal-concept audit (16 concepts, footprint Jaccard 0.048; 474 and 0.610 at |H| <= 15)
- the MPLE ladder and the transitive-triple check
- the role-assignment metrics and the footprint-survival strata

## What is new

| Analysis | Script | Output |
|---|---|---|
| Replications: 116th and 117th Senate, 118th House | `src/run_case.py` | `results/<case>/summary.json` |
| Sponsor-activity, co-sponsor-popularity and same-party baselines with paired intervals | `src/report.py` | `summary.json` |
| Bipartisan vs single-party coalitions | `src/report.py` | `summary.json`, Table `r3` |
| "Neither footprint survives" stratum | `src/report.py` | Table `a5b` |
| Exact joint footprint probability L_J (2^|F| enumeration) | `src/run_joint.py` | `results/s118_joint/` |
| Head cap 3 sensitivity | `src/run_case.py s118cap3` | `results/s118cap3/` |
| Training on the uncapped projection | `src/run_case.py s118uncap` | `results/s118uncap/` |
| Arc-level diagnostic over 30 splits; transitive-triple check | `src/extras.py` | `results/s118_extras/` |
| Concept audit in all cases | `src/concept_audit.py` | `results/concepts_all.json` |
| MPLE validation against `ergm` and simulation from the MPLE fits | `r/simulate_from_mple_senate.R` | `results/mple_simulation/` |
| MCMC-MLE from a contrastive-divergence start, with goodness of fit | `r/mcmcmle_cd_senate.R` | `results/mcmcmle_cd/` |
| MCMC-MLE from the MPLE start (fails to mix for M4c; kept for the record) | `r/mcmcmle_gof_senate.R` | — |

The output paths in the table are working paths. The identifier-free aggregates
committed in `results/` are:

- `summary_{s118,s117,s116,h118,s118cap3,s118uncap}.json`: per-case metrics, contrasts, role, strata and bipartisan results
- `concept_audit.json`
- `s118_joint_footprint_scores.json`
- `s118_ttriple_and_arc_diagnostic.json`
- `mple_simulation/`
- `tables/` (LaTeX)
- `figures/`

## Data (not in the repository)

All inputs are public. Download them into one folder (`RAW` in `src/runlib.py`):

- GPO Bill Status bulk XML:
  - `https://www.govinfo.gov/bulkdata/BILLSTATUS/{116,117,118}/s/BILLSTATUS-{116,117,118}-s.zip`
  - `https://www.govinfo.gov/bulkdata/BILLSTATUS/118/hr/BILLSTATUS-118-hr.zip`
- `legislators-current.yaml` and `legislators-historical.yaml` from https://github.com/unitedstates/congress-legislators
- Voteview member files: `https://voteview.com/static/data/out/members/{S,H}{114..118}_members.csv`

## Running

```bash
cd revision_nov2026/src
export REVISION_RAW=/path/to/raw REVISION_PROC=/path/to/processed   # defaults: data/raw|processed/revision_nov2026
python -I parse_billstatus.py RAW/BILLSTATUS-118-s.zip PROC/bills_118-s.json   # likewise for the other archives
python run_case.py s118 ../results/s118      # also s117, s116, h118, s118cap3, s118uncap
python report.py  s118 ../results/s118
python extras.py s118 ../results/s118_extras ../results/r_export_s118
python concept_audit.py ../results/concepts_all.json s118 s117 s116 h118
python run_joint.py s118 ../results/s118 ../results/s118_joint MCAR 1 10
python make_tables.py ../results TABLE_DIR
python make_figures.py ../results FIGURE_DIR
Rscript ../r/simulate_from_mple_senate.R ../results/r_export_s118 ../results/mple_simulation
Rscript ../r/mcmcmle_cd_senate.R ../results/r_export_s118 ../results/mcmcmle_cd M5
python -m pytest ../tests
```

A 118th Senate case takes about 3 minutes for all 60 splits on one core. The House takes about 10 minutes.

## Model notes

- Change statistics follow statnet `ergm` definitions with fixed decay 0.5:
  `edges`, `mutual`, `gwodegree`, `gwidegree`, `dgwesp` (OTP, OSP, ISP), `ctriple`,
  `nodematch`, `absdiff`, `nodeocov`.
  The tests check every change statistic against brute-force toggles.
- MPLE is an unpenalised logistic regression on all ordered dyads. A negligible ridge (1e-8) is added for numerical stability.
  On the complete 118th Senate projection the M4c and M5 coefficients agree with `ergm` 4.12 to four decimal places.
- The joint footprint score is log Pr(Y_F = 1 | Y_-F), computed exactly by Gray-code enumeration of the 2^|F| footprint configurations.

## Privacy

Published outputs are aggregates. No actor identifiers, event rows or candidate panels are written to `results/` in this folder.
