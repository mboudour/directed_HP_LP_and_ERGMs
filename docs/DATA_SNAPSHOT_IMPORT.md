# Exact data snapshot imported for autonomous computation

## Source snapshot

- Google Drive archive: `data.zip` from the user-shared project folder.
- Imported archive filename: `directed_hp_ergms_data_20261015.zip`.
- Archive byte size: `2,211,008,512` bytes (2.21 GB decimal).
- SHA-256: `c518f2932cb389d0705f25abebf393dde9e49fc2990d881642cf40f95677305e`.
- Import date: 2026-10-15.

The archive is retained unchanged outside the Git working tree as the sealed source snapshot. Its `data/` tree was extracted after rejecting path-traversal members. The ZIP contained 26 normal macOS `__MACOSX/` metadata entries; those entries are excluded from the computational working copy and do not alter the substantive data.

## Verified attached working copy

| Data subtree | Files | Bytes |
|---|---:|---:|
| `data/raw/` | 517,470 | 2,333,759,381 |
| `data/external/` | 11 | 1,002,707,428 |
| `data/interim/` | 9 | 160,488,463 |
| `data/processed/` | 23 | 3,490,802 |
| `data/metadata/` | 35 | 89,221 |

The working copy was verified by identical relative file paths and file sizes against the preserved extracted snapshot in every listed data subtree.

## Repository policy

Raw, external, interim, and processed data remain ignored by Git. The repository tracks only the import provenance record, source code, configurations, data-audit metadata that are appropriate to publish to the private repository, and aggregate computational outputs. No email contents, row-level data, source archives, or raw prediction panels are committed.
