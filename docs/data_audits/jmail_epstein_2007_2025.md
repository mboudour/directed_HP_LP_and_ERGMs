# Jmail / Epstein email records, 2007–2025

## Local source and project copy

- Original local source:
  `/Users/moses/WorkPlaces/Sharebox3/WorkingProjects/0. Accepted Articles/Missing Links in Public Email and Covert Networks via Supervised Hyperlink Prediction/EPJDS initial submission/data/Epstein_emails_from_jmail_ALL_chrs.csv`
- Project copy:
  `data/raw/jmail_epstein_2007_2025/Epstein_emails_from_jmail_ALL_chrs.csv`
- Retrieved into this project: 2026-10-13
- SHA-256:
  `0708ba177d6f831a81d002b0652c63bb0bd9d0c5d511081ab35df7ee86f44767`

## Raw record unit

One CSV row records one directed sender–recipient email relation with fields:

- `SENDER`
- `RECIPIENT`
- `DATE`
- `CONTENT`
- `No. of characters`

The file contains 7,764 rows.

## Direction and higher-order status

- Direction means `SENDER → RECIPIENT`.
- The file supports directed dyadic graph construction and time-based analysis.
- It does not include a documented message identifier or complete recipient list.
- Therefore it does not support native multi-recipient event recovery without a separately justified message-bundling procedure.

## Supported project targets

- Directed arc recovery: yes.
- Directed footprint completion: yes, after aggregation.
- Formal-concept recovery: yes, after aggregation.
- Native-event recovery: no.
- Conditional role assignment: directed dyadic form only.

## Processing constraints

- Preserve the raw CSV unchanged.
- Deduplicate and normalize sender/recipient entities only in a versioned derived-data pipeline.
- Treat content as restricted source material; do not commit the raw file to Git.
- Retain the original date field for later temporal-window checks.
