# Jmail v1 admissibility source note

Jmail v1 makes a 1.78-million-row structured email derivative available as
Parquet. The slim variant retains sender, recipient arrays, send time, source
account, document/drop identifiers, and release metadata while omitting bodies;
this makes it technically suitable for a conservative header-based native-event
audit.[1]

The provider describes three provenance streams: House Oversight releases,
Department of Justice releases, and Yahoo-account emails added from DDoSecrets
in collaboration with Drop Site News.[2] The client README describes the data as
public-domain US-government records, but that broad statement does not itself
resolve the provenance or reuse status of every Yahoo/DDoSecrets-derived record.
The first research stage must therefore preserve source identifiers and let an
explicit gate separate or exclude any provenance stream that cannot support the
paper's analysis and release policy.[3]

**Audit result and current decision.** The no-body, no-event audit completed:
all 1,781,028 message IDs are nonempty and unique, 180,572 records (10.139%)
lack a sender, 5,023 (0.282%) have an invalid or missing timestamp, and
1,120,328 (62.903%) satisfy the provisional singleton-sender, To-plus-Cc
candidate rule. This establishes technical feasibility for a restricted event
view but not research admissibility. Native events, entity-resolution rules,
Bcc handling, source-stream inclusion, and any public derived release remain
blocked until the explicit gate is approved.

**References**

[1]: https://jmail.world/docs/datasets "Jmail Data API datasets"
[2]: https://jmail.world/docs/introduction "Jmail Data API introduction"
[3]: https://github.com/cappy-dev/jmail-client/blob/main/README.md "Jmail Client README"
