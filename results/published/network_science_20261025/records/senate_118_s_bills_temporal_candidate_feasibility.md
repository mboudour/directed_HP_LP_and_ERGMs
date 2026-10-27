# Senate temporal-feasibility constraints for random negative coalitions

The event-first masks, observed training projections, and source-positive records are frozen. This audit applies a corrected rule only to synthetic random negative coalitions: every candidate participant must have a Senate roster interval satisfying ``term_start <= introduction_date < term_end`` for every distinct introduction date associated with its paired positive ordered event type.

## Source-positive roster coverage QA

- Native event records checked: `4,374`
- Records whose every participant is service-covered at their introduction date: `4,373`
- Records with one or more roster-date exceptions: `1`
- Participant appearances checked: `23,232`
- Service-covered participant appearances: `23,231`
- Participant appearances outside recorded roster coverage: `1`

The source-positive exception is retained and documented; it is not silently removed from the source-defined target. The co-service rule instead prevents synthetic negatives from combining actors who cannot jointly occupy the Senate at every date associated with the positive event type.

## Cap-specific sidecars

| Head cap | Eligible records | Ordered types | Recurrent types | Types with >1 date | Distinct type-date pairs | Type IDs checked against frozen masks |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 2,976 | 2,240 | 381 | 367 | 2,913 | 134,400 |
| 10 | 3,956 | 3,209 | 388 | 369 | 3,884 | 192,540 |

## Superseded random-panel audit before correction

| Head cap | Mask | Synthetic negatives | Date-infeasible | Share |
|---:|---|---:|---:|---:|
| 3 | mcar | 20,100 | 977 | 4.86% |
| 3 | mnar_out | 20,221 | 948 | 4.69% |
| 10 | mcar | 28,844 | 1,917 | 6.65% |
| 10 | mnar_out | 28,957 | 2,004 | 6.92% |

The sidecars do not contain participant identities. They map only frozen canonical event-type identifiers to all associated introduction dates and preserve a hash-based provenance record for the public source snapshots.
