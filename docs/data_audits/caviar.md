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

The publisher confirms directed, valued communication ties but does not state on the download page whether matrix rows represent caller-to-receiver or receiver-to-caller.

Therefore, caller-to-receiver orientation is currently unconfirmed. The data are retained for audit, but they are not eligible for directed evaluation until the orientation is verified from the underlying documentation or an authoritative source.

## Provisional supported targets

Once direction is verified:

- Directed arc recovery: yes.
- Directed footprint completion: yes.
- Formal-concept recovery: yes, after binary aggregation.
- Native-event recovery: no.
- Conditional role assignment: directed dyadic form only.

## Processing constraints

- Preserve all published matrices unchanged.
- Do not commit the archives or raw matrices to Git.
- Retain valued matrices for the planned valued-ERGM sensitivity analysis.
- Create a documented binary version only in a derived-data pipeline.
