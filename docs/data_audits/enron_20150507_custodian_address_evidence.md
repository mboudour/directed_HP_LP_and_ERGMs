# Enron custodian-address evidence audit

## Scope

This audit collects evidence from sent-like maildir folders only. It does **not** map
addresses to custodians, resolve aliases, filter records, or construct events.

- Custodian mailboxes: `150`
- Custodians with sent-like files: `149`
- Sent-like files: `126,591`
- Eligible single-sender evidence files: `126,588`
- Custodians with any eligible sender evidence: `149`
- Custodians with a unique top candidate: `149`
- Unique top candidates supported by at least 90% of a custodian's evidence:
  `112`
- Custodians without eligible evidence: `1`

## Evidence rule

A row contributes one vote for a candidate sender address only when it is in a sent-like
folder, has exactly one syntactically valid From address, and has no From-address parsing
issue. The sent-like taxonomy rule is: `sent, sentitem, sentitems, sentmail`.

The detailed CSV contains only the top three candidate addresses per custodian, with
support counts and shares. It is an audit table, not a final identity map.
