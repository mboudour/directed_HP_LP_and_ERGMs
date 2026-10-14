# Enron custodian-mapping confidence profile

## Scope

This audit profiles the rank-one candidate address for each custodian. It does not assign
an address to a custodian, resolve aliases, or create an event table.

- Source custodian mailboxes: `150`
- Rank-one candidate mappings: `149`
- Custodians without a rank-one candidate: `1`
- Candidate addresses shared by multiple custodians: `1`
- Custodians involved in a shared-address collision:
  `2`

## Rank-one support distribution

| Support share | Custodians |
|---|---:|
| 100% | 79 |
| 99–<100% | 24 |
| 95–<99% | 4 |
| 90–<95% | 5 |
| 75–<90% | 22 |
| 50–<75% | 14 |
| <50% | 1 |

## Threshold counts

| Requirement | Custodians |
|---|---:|
| At least 100% | 79 |
| At least 99% | 103 |
| At least 95% | 107 |
| At least 90% | 112 |
| At least 75% | 134 |
| At least 50% | 148 |

The lowest rank-one support share is `0.421`. The median is
`1.000`. The smallest gap between first- and second-ranked
candidate support is `3` message files.

## Interpretation

This profile informs a later documented mapping policy. A high support share alone is not
an identity proof, and a shared top candidate across mailbox directories must be resolved
or excluded explicitly. No mapping has been frozen by this script.
