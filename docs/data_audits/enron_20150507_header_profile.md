# Enron header-profile audit

## Scope

This audit profiles the header-only intermediate table. It does not remove, merge, or
alter messages. It does not retain any message body or header content in the anomaly
register.

- Input records: `517,401`
- Header parse errors: `12`
- Total parser defects: `30`
- Truncated headers: `0`
- Unterminated headers: `0`
- Anomalous records: `12`

## Duplicate indicators — not yet a deduplication decision

| Indicator | Unique values | Duplicate groups | Records in duplicate groups | Extra records beyond first |
|---|---:|---:|---:|---:|
| Exact raw SHA-256 | 517,401 | 0 | 0 | 0 |
| Non-missing Message-ID | 517,389 | 0 | 0 | 0 |

Exact raw SHA-256 duplicates are byte-identical raw message files. Repeated `Message-ID`
values are reported separately because they can indicate copies, retransmissions, or reuse;
they will not be removed without an explicit policy.

## Header-missingness patterns

| Missing fields | Records |
|---|---:|
| cc_raw, bcc_raw | 369,135 |
| none | 126,407 |
| to_raw, cc_raw, bcc_raw | 20,382 |
| to_raw | 1,465 |
| message_id_raw, date_raw, from_raw, to_raw, cc_raw, bcc_raw | 12 |

## Privacy-preserving anomaly register

`data/interim/enron_20150507/audits/enron_20150507_header_anomaly_register.csv` contains source paths,
sizes, hashes, and parsing flags only. It contains no message body, address, date, or
subject content.
