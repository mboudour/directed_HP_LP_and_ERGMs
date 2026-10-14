# Enron parsed-header audit

## Scope

This is a syntactic normalization stage. It keeps all `517,401` source records
and performs no message deduplication, alias resolution, recipient-policy choice, or event
construction.

- Input: `data/interim/enron_20150507/message_headers.parquet`
- Output: `data/interim/enron_20150507/parsed_headers.parquet`

## Date parsing

| Status | Records |
|---|---:|
| Timezone-aware and converted to UTC | 517,389 |
| Timezone missing; retained as naive datetime | 0 |
| Invalid date header | 0 |
| Missing date header | 12 |

Earliest timezone-aware timestamp: `1980-01-01T00:00:00+00:00`
Latest timezone-aware timestamp: `2044-01-04T22:48:58+00:00`

## Address parsing

| Header | Messages with one or more usable addresses | Parsing issues |
|---|---:|---:|
| From | 517,386 | 1 |
| To | 495,487 | 89 |
| Cc | 127,864 | 4 |
| Bcc | 127,864 | 4 |

Address parsing only lowercases syntactically usable addresses. It does not map aliases,
mailboxes, or organizations to actors. To, Cc, and Bcc are still separate because the
recipient policy has not yet been chosen.
