# CAVIAR covert communication network

## Source and local acquisition

- Dataset source: Analytic Technologies / UCINET covert-network archive
- Dataset page: https://sites.google.com/site/ucinetsoftware/datasets/covert-networks/caviar
- Download folder: https://drive.google.com/drive/folders/1kPA4rxxDHbQaDTEk_6NXuiaw9k-ctqgo
- Retrieved: 2026-10-13
- Investigation: Project Caviar, Montreal hashish and cocaine importation network, 1994–1996.
- Published network: 110 actors, communication data from police wiretaps.

## Original archives

- CSV archive:
  `data/external/caviar/Caviar/Caviar CSV_v2.zip`
- CSV archive SHA-256:
  `8fcdbcdd6634635309cfc464c476ac9ce520697de22474e4eee353a039c1dca2`
- UCINET archive:
  `data/external/caviar/Caviar/Caviar_v2.zip`
- UCINET archive SHA-256:
  `c20b42713ffad6613d737fa185fea1c3b6f8137d78ac490b8de5b9cec89df71f`

## Raw matrices

- CSV matrices:
  `data/raw/caviar/csv_matrices/`
- UCINET matrices:
  `data/raw/caviar/ucinet_matrices/`
- Contents:
  11 phase-specific person-by-person matrices (`CAVIAR1` through `CAVIAR11` ) and one full-network matrix (`CAVIAR_FULL` / `Caviar_full`).
- Matrix type:
  directed and valued communication ties. Values represent communication activity.

## Direction and use condition

The publisher confirms directed, valued communication ties but does not state on the download page whether matrix rows represent caller-to-receiver or receiver-to-caller. A peer-reviewed analysis of the same Project Caviar data states explicitly that links point from the caller to the receiver: Anastasiadis and Antoniou (2024), Section 3.1, https://www.mdpi.com/2078-2489/15/2/84.

The local gate record `data/metadata/gates/caviar_direction.json` therefore approves **only** the full 110-node static matrix `CAVIAR_FULL.csv` with rows as callers/senders and columns as receivers. It records the provenance and exact source limitation.

The 11-phase sequence is not approved for directed or temporal processing. `CAVIAR7.csv` repeats actor label `9` at two positions, and the paired UCINET header repeats the same label. No authoritative correction identifies the duplicated position, so the source is preserved unchanged and no labels are merged, imputed, or silently renamed.

## Provisional supported targets

For the approved full static matrix:

- Directed arc recovery: yes.
- Directed footprint completion: yes.
- Formal-concept recovery: yes, after binary aggregation.
- Native-event recovery: no.
- Conditional role assignment: directed dyadic form only.

For the phase series: no directed, temporal, or panel-based target is currently supported.

## Processing constraints

- Preserve all published matrices unchanged.
- Do not commit the archives or raw matrices to Git.
- Retain valued matrices for the planned valued-ERGM sensitivity analysis.
- Create a documented binary version only in a derived-data pipeline.
