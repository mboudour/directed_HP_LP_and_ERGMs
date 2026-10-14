# Enron address-level native-event build

## Scope

This build creates an address-level native-event table from normalized message headers.
No email addresses are placed in the tracked summary or audit report; the event table
remains local and ignored by Git.

- Input header records: `517,401`
- Native events written: `490,141`
- Unique address-level nodes: `86,408`
- Earliest event timestamp: `1980-01-01T00:00:00+00:00`
- Latest event timestamp: `2044-01-04T22:48:58+00:00`

## Header policy

Each retained event has one sender and a non-empty recipient head built from the ordered,
deduplicated union of To and Cc. Bcc is excluded because its non-empty values are exact
copies of Cc in this archive. If the sender appears in To or Cc, that self-address is
removed from the head to enforce tail-head disjointness; all other recipients remain.

No alias resolution is applied: nodes are canonical email addresses at this stage.

## Sequential exclusions

| First unmet requirement | Records |
|---|---:|
| date not timezone aware | 12 |
| sender not exactly one clean address | 3 |
| to or cc address parse issue | 71 |
| no to or cc recipient | 20,400 |
| head empty after sender removal | 6,774 |

## Recipient-head arity

| Head size | Native events |
|---|---:|
| 1 | 274,380 |
| 2 | 53,094 |
| 3 | 28,912 |
| 4 | 19,043 |
| 5+ | 114,712 |

## Provenance

- Event identifier: `enron_20150507:` followed by the raw-message SHA-256.
- Time: original timezone-aware Date header converted to UTC.
- Body content: never retained.
- Event table: `data/interim/enron_20150507/native_events_address_level.parquet`.
