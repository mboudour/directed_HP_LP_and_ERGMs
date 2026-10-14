# Enron event-candidate header audit

## Scope

This is a descriptive profile only. It does not create, exclude, merge, or deduplicate
events. It does not resolve email aliases or restrict the actor set to custodian mailboxes.

- Records profiled: `517,401`
- Timezone-aware timestamps: `517,389`
- Strict primary To-plus-Cc candidates: `458,211`
- Strict Bcc candidates: `108,449`

A strict candidate is defined only for audit purposes: exactly one parsed sender, a
timezone-aware date, at least one recipient, no sender-recipient self-overlap, and no
address parsing issue.

## Recipient-header overlap

| Aggregate check | Messages |
|---|---:|
| To and Cc share at least one recipient | 11,454 |
| To and Bcc share at least one recipient | 11,454 |
| Cc and Bcc share at least one recipient | 127,864 |
| Both Cc and Bcc are non-empty | 127,864 |
| Non-empty Cc and Bcc recipient sets are exactly equal | 127,864 |

No recipient header is silently discarded here. The primary analysis policy remains
provisional: To plus Cc, with Bcc excluded from the public primary network and retained
as a separately documented sensitivity field.

## Additional checks

| Check | Messages |
|---|---:|
| Sender appears in its own To-plus-Cc recipient set | 38,708 |
| Records with one or more address parsing issues | 72 |
| Total address parsing issues | 98 |
