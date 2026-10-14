# Enron Bcc-header audit

## Result

**Confirmed: every non-empty extracted Bcc header is exactly equal to its extracted Cc header.**

## Aggregate counts

| Header condition | Records |
|---|---:|
| Cc non-empty | 127,872 |
| Bcc non-empty | 127,872 |
| Both Cc and Bcc non-empty | 127,872 |
| Cc only | 0 |
| Bcc only | 0 |
| Both non-empty and exactly equal | 127,872 |

## Interpretation

This check uses `cc_raw` and `bcc_raw` from the extracted-header table, before address
normalization. Therefore, exact equality cannot have been created by lowercase conversion,
within-header deduplication, or recipient-set construction.

If confirmed, Bcc is a corpus-export duplicate of Cc rather than an independent recipient
field. The Enron primary event policy is then one sender and the deduplicated union of To
and Cc recipients. Bcc is excluded rather than presented as a misleading sensitivity
analysis.
