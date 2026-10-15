# Citation topic: email-Eu-core temporal network provenance and proper dataset citation

## Recommended sources

### 1. Official temporal dataset record (use this for dataset identity and provenance)

**Ashwin Paranjape, Austin R. Benson, and Jure Leskovec.** 2017. *email-Eu-core temporal network*. Stanford Large Network Dataset Collection (SNAP), official dataset record. DOI: **[none assigned]**. URL: <https://snap.stanford.edu/data/email-Eu-core-temporal.html>.

The SNAP record is the authoritative source for the released artifact used by the manuscript. It says that the network was generated from anonymized incoming and outgoing email among members of a large European research institution; it defines each event as a directed edge `(u, v, t)` where `u` sent an email to `v` at time `t`; it states that a separate edge is created for each recipient; and it gives the released data format `SRC DST UNIXTS`. It reports 986 nodes, 332,334 temporal edges, 24,929 edges in the static graph, and an 803-day span for `email-Eu-core-temporal`.

**Manuscript claim supported:** the data are native directed, timestamped email events, and the manuscript's temporal diagnostic is based on the official temporal release. The record also supports reporting the exact release-level counts and the fact that the temporal static graph is the largest weakly connected component of the `email-Eu-core` network. It does **not** support claims about neural benchmarks, full forecasting, MCMC-derived joint L3 evidence, or the missingness mechanism used in this manuscript; those are the manuscript's own design choices.

### 2. Official source publication named by the temporal SNAP record

**Ashwin Paranjape, Austin R. Benson, and Jure Leskovec.** 2017. “Motifs in Temporal Networks.” *Proceedings of the Tenth ACM International Conference on Web Search and Data Mining (WSDM ’17)*, 601–610. Association for Computing Machinery. DOI: **[10.1145/3018661.3018731](https://doi.org/10.1145/3018661.3018731)**. Publisher record: <https://dl.acm.org/doi/10.1145/3018661.3018731>.

ACM verifies the authors, title, WSDM ’17 venue, publication date (2 February 2017), pages 601–610, and DOI. The paper develops temporal-network motifs from timestamped links and uses real-world temporal networks for motif counting. SNAP explicitly names this paper as the source citation for `email-Eu-core-temporal`.

**Manuscript claim supported:** this is the peer-reviewed source citation that should accompany use of the temporal SNAP release, and it supports the manuscript's limited statement that the release is a timestamped temporal-network dataset suitable for a bounded temporal diagnostic. It should not be cited as evidence that the paper performed directed link prediction, ERGM MPLE, MCAR/MNAR masking, or forecasting; it did not establish those claims.

### 3. Official static SNAP record (use when describing the static projection separately)

**Jure Leskovec / Stanford SNAP.** *email-Eu-core network*. Stanford Large Network Dataset Collection, official dataset record. DOI: **[none assigned]**. URL: <https://snap.stanford.edu/data/email-Eu-core.html>.

The static record defines an edge `(u,v)` as at least one email sent from person `u` to person `v`, reports 1,005 nodes and 25,571 directed edges, and describes the 42 department labels. It also warns that the temporal release's static graph is the largest weakly connected component and that node IDs do not correspond to the same node IDs in the entire static network.

**Manuscript claim supported:** any separate statement about the full static `email-Eu-core` release, its directed one-or-more-email edge definition, its department labels, or the distinction between the 1,005-node static release and the 986-node temporal component. Do not use it to claim that the full static release contains event timestamps or that its node IDs are interchangeable with the temporal release.

## Citation and provenance guidance

For the temporal experiments, cite both the official temporal SNAP record and Paranjape–Benson–Leskovec (2017, DOI above). Cite the static SNAP record only where the manuscript discusses the separate static release or explicitly explains the temporal release's component relationship. Preserve the dataset's native event semantics: a timestamped directed email event from sender to recipient. Any collapsed static graph, score, MCAR/MNAR-out mask, ERGM MPLE conditional footprint, or other transformation should be labeled as an analysis-derived representation rather than dataset provenance.

## Limitations

The official SNAP pages do not assign a DOI and do not identify the institution by name or provide the raw server-log provenance in greater detail. Therefore this note does not infer an institution, collection dates beyond the released temporal span, or a one-to-one identity with another email dataset. The Ebel–Mielsch–Bornholdt email-network paper (Phys. Rev. E 66, 035103, DOI 10.1103/PhysRevE.66.035103) is a real peer-reviewed email-network study, but it is not needed for the exact SNAP citation and should not be used here to assert that it is the provenance of this specific `email-Eu-core-temporal` release without additional evidence.

## Verification URLs

- Official temporal record: <https://snap.stanford.edu/data/email-Eu-core-temporal.html>
- Official static record: <https://snap.stanford.edu/data/email-Eu-core.html>
- ACM publisher record: <https://dl.acm.org/doi/10.1145/3018661.3018731>
- SNAP collection citation guidance: <https://snap.stanford.edu/data/>
