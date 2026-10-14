# Ciel covert communication network

## Source and local acquisition

- Dataset source: Analytic Technologies / UCINET covert-network archive.
- Dataset page:
  https://sites.google.com/site/ucinetsoftware/datasets/covert-networks/cielnet
- Download folder:
  https://drive.google.com/drive/folders/1jB_xVR8DwijSPEcyU7wgfiTTEgN1L5r9
- Retrieved: 2026-10-13.
- Investigation: Project Ciel, a Montreal drug-importation network investigated from May 1996 to June 1997.
- Published network: 25 participants; communication information obtained through police wiretaps.

## Original archives

- CSV archive:
  `data/external/ciel/CielNet/CielNet CSV.zip`
- CSV archive SHA-256:
  `ebc423fa4448ec542ad63bc333da23ea24c5f60635e3853ac90650386e512fef`
- UCINET archive:
  `data/external/ciel/CielNet/CielNet.zip`
- UCINET archive SHA-256:
  `10309807e71176228c0834e64a9280f845f569fda90cfa93b7cf1b5d470e252d`

## Raw matrices

- CSV matrix:
  `data/raw/ciel/csv_matrix/CSV/CIELNET.csv`
- UCINET matrix and header:
  `data/raw/ciel/ucinet_matrix/CielNet/CielNet.##d`
  `data/raw/ciel/ucinet_matrix/CielNet/CielNet.##h`
- Matrix type: 25 × 25 directed, valued person-by-person communication matrix.
- Values: communication activity; higher values represent more active communication channels.

## Direction and use condition

The source confirms directed, valued communication ties, but it does not explicitly state whether rows are caller-to-receiver or receiver-to-caller.

Therefore, caller-to-receiver orientation is currently unconfirmed. The data are retained for audit, but are not eligible for directed evaluation until this semantic direction is verified from an authoritative source.

## Provisional supported targets

Once direction is verified:

- Directed arc recovery: yes.
- Directed footprint completion: yes.
- Formal-concept recovery: yes, after binary aggregation.
- Native-event recovery: no.
- Conditional role assignment: directed dyadic form only.

## Processing constraints

- Preserve both published archives and both matrix representations unchanged.
- Do not commit the archives or raw matrices to Git.
- Retain values for possible valued-ERGM sensitivity analysis.
- Create a binary derived network only in a documented pipeline.
