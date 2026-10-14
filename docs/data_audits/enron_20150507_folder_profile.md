# Enron maildir-folder taxonomy audit

## Scope

This audit examines maildir folder labels only. It does not parse address content, infer
custodian identities, create event records, or apply any filter.

- Records profiled: `517,401`
- Custodian mailboxes: `150`
- Unique folder paths: `1,940`
- Sent-like message files: `126,591`
- Custodians with sent-like files: `149`

The provisional sent-folder rule flags any folder-path component that normalizes to one of:
`sent, sentitem, sentitems, sentmail`. It is an audit flag only, not yet a mapping rule.

## Twenty most frequent top-level folder labels

| Top-level folder | Message files |
|---|---:|
| `all_documents` | 128,103 |
| `discussion_threads` | 58,609 |
| `sent` | 57,653 |
| `deleted_items` | 51,356 |
| `inbox` | 44,859 |
| `sent_items` | 37,921 |
| `notes_inbox` | 36,665 |
| `_sent_mail` | 30,109 |
| `calendar` | 6,133 |
| `archiving` | 4,477 |
| `_americas` | 4,021 |
| `personal` | 2,577 |
| `attachments` | 2,026 |
| `meetings` | 1,872 |
| `c` | 1,656 |
| `schedule_crawler` | 1,398 |
| `chris_stokley` | 1,252 |
| `logistics` | 1,192 |
| `archive` | 1,179 |
| `tw_commercial_group` | 1,159 |

## Twenty most frequent sent-like folder paths

| Folder path | Message files |
|---|---:|
| `sent` | 57,653 |
| `sent_items` | 37,920 |
| `_sent_mail` | 30,109 |
| `chris_stokley/sent` | 515 |
| `_sent` | 265 |
| `deleted_items/_sent_mail` | 128 |
| `sent_items/clickathome` | 1 |

## Next decision

The next stage will use an explicit, recorded sent-folder rule to gather candidate sender
addresses for each custodian mailbox. It will report confidence and ambiguity rather than
silently mapping addresses to custodians.
