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
The first research stage must therefore profile the local source without
materialising events, preserve source identifiers, and let an explicit gate
separate or exclude any provenance stream that cannot support the paper's
release and analysis policy.[3]

**Current decision.** The source passes no admissibility gate merely by being
publicly downloadable. The next executable step is a no-body, no-event audit of
IDs, sender/recipient headers, timestamps, duplicate IDs, and the candidate
To-plus-Cc event count. Native events, entity-resolution rules, Bcc handling,
and any public derived release remain blocked until the audit and source-policy
decision are recorded.

**References**

[1]: https://jmail.world/docs/datasets "Jmail Data API datasets"
[2]: https://jmail.world/docs/introduction "Jmail Data API introduction"
[3]: https://github.com/cappy-dev/jmail-client/blob/main/README.md "Jmail Client README"
