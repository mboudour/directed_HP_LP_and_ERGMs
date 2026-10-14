# SNAP email-Eu-core temporal network

## Source and local acquisition

- Official publisher: Stanford Network Analysis Project (SNAP)
- Dataset page: https://snap.stanford.edu/data/email-Eu-core-temporal.html
- Archive URL: https://snap.stanford.edu/data/email-Eu-core-temporal.txt.gz
- Retrieved: 2026-10-13
- Archive location:
  `data/external/email_eu_core_temporal/email-Eu-core-temporal.txt.gz`
- Archive SHA-256:
  `f6cc93249978e59d1aba111b55ea10ec553917419a3be1210012b5db3580efa6`
- Uncompressed raw-file location:
  `data/raw/email_eu_core_temporal/email-Eu-core-temporal.txt`
- Expected and verified temporal-row count:
  `332334`

## Raw record unit and direction

Each row has three space-separated fields:

`SRC DST UNIXTS`

A row `(u, v, t )` means that user `u` sent one email to user `v` at Unix time `t`.

SNAP creates one separate row for each recipient of an email. The full network has 986 nodes, 332,334 temporal rows, 24,929 static directed arcs, and an 803-day time span.

## Higher-order status

- No message identifier is supplied.
- Recipient bundles cannot be recovered directly.
- Same-sender/same-timestamp records may be assessed later as a sensitivity analysis only; they are not treated as native events in the main design.

## Supported project targets

- Directed arc recovery: yes.
- Directed footprint completion: yes.
- Formal-concept recovery: yes, after aggregation.
- Native-event recovery: no.
- Conditional role assignment: directed dyadic form only.

## Processing constraints

- Preserve the `.txt.gz` archive and uncompressed source file unchanged.
- Do not commit either source file to Git.
- Aggregate to a binary directed graph only in a documented derived-data pipeline.
- Retain timestamps for chronological and aggregation-window checks.
