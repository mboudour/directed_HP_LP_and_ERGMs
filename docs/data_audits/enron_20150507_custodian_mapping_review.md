# Enron custodian-mapping review bundle

## Scope

This script prepares a local review table for ambiguous custodian-address evidence. It
assigns no address to a custodian, filters no message, and creates no event table.

- Source custodian mailboxes: `150`
- Provisionally high-confidence candidates: `110`
- Custodians requiring review: `40`
- No rank-one candidate: `1`
- Top support below 90%: `37`
- Top address shared by multiple custodians: `2`

## Local review table

The local-only table is written to
`data/interim/enron_20150507/audits/enron_20150507_custodian_mapping_review.csv`.
It includes the top three candidate addresses and their support for each flagged
custodian. It remains ignored by Git because it contains email addresses.

## Review rule

A custodian is included in this review bundle if it has no rank-one candidate, has
rank-one support below `90%`, or shares its rank-one address with
another custodian. The threshold is an audit triage rule only; it is not a final
identity-resolution decision.
