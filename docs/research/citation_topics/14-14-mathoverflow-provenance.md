# MathOverflow / Stack Exchange data provenance and proper dataset citation

**Topic.** Provenance and citation for MathOverflow interaction data used in directed link/hyperlink prediction under missingness.

## Recommended sources

### [1] Stanford SNAP dataset record (primary record for the derived network)

- **Authors:** Stanford Network Analysis Project (SNAP)
- **Year:** n.d. (dataset page; access date should be recorded by the manuscript)
- **Title:** *Math Overflow temporal network*
- **Venue:** SNAP Network Data Sets, Stanford University
- **DOI:** none listed
- **URL:** <https://snap.stanford.edu/data/sx-mathoverflow.html>
- **Source type:** Official dataset repository/record

**What it supports.** This record is the authoritative citation for the downloadable `sx-mathoverflow` network files and their construction. It explicitly defines the directed timestamped edge `(u,v,t)` as (i) user `u` answering user `v`’s question, (ii) user `u` commenting on user `v`’s question, or (iii) user `u` commenting on user `v`’s answer; it identifies the union graph and the three component files; it states that the graphs were constructed from the Stack Exchange Data Dump; and it specifies that node IDs correspond to the dump’s `OwnerUserId` field. It also gives the `SRC DST UNIXTS` file format. These statements support the manuscript’s provenance note and its claim that the native data are directed, timestamped user interactions. They do **not** support claims about the manuscript’s MCAR/MNAR masks, ERGM estimation, prediction performance, or any neural benchmark.

### [2] Internet Archive data record (snapshot actually containing MathOverflow XML)

- **Authors:** Internet Archive (repository record; uploaded by Franck Dernoncourt)
- **Year:** 2023
- **Title:** *Stack Exchange Data Dump — 2023-03-08*
- **Venue:** Internet Archive, Dataset Collection
- **DOI:** none listed
- **URL:** <https://archive.org/details/stack-exchange-data-dump-2023-03-08>
- **Source type:** Official public repository record / dated data snapshot

**What it supports.** The record identifies the dated dump (`stack-exchange-data-dump-2023-03-08`), lists a `mathoverflow.net.7z` file and a separate `meta.mathoverflow.net.7z` file, and records the repository’s Attribution-ShareAlike 4.0 metadata. Cite this item only if this is the exact dump snapshot used to derive or audit the manuscript’s MathOverflow data; otherwise replace it with the exact dated dump record used. It supports reproducible identification of the raw site export and its recorded license metadata. It does **not** by itself establish the semantics of the derived directed interaction edges, the SNAP preprocessing, or any temporal-network statistics.

### [3] Paranjape, Benson, and Leskovec (2017) (underlying published dataset/method citation)

- **Authors:** Ashwin Paranjape; Austin R. Benson; Jure Leskovec
- **Year:** 2017
- **Title:** “Motifs in Temporal Networks”
- **Venue:** *WSDM ’17: Proceedings of the Tenth ACM International Conference on Web Search and Data Mining*, pp. 601–610
- **DOI:** `10.1145/3018661.3018731`
- **URL:** <https://doi.org/10.1145/3018661.3018731>
- **Source type:** Peer-reviewed conference paper / publisher record

**What it supports.** The ACM publisher record verifies the authors, title, venue, pages, publication date, and DOI. The SNAP MathOverflow record names this paper as the source citation for the MathOverflow temporal-network dataset. Therefore, the manuscript should cite this paper when referring to the published temporal-network source underlying the SNAP release (and to the temporal-network motif context). It does **not** justify calling the present study a motif study, a neural benchmark, a joint MCMC analysis, or a full forecasting evaluation; nor does it replace citation of the exact raw-dump snapshot.

## Citation practice for the manuscript

For a reproducible provenance statement, cite **[1]** for the derived `sx-mathoverflow` files and edge semantics, **[3]** for the published source named by the dataset record, and **[2]** only when the 2023-03-08 raw dump is the actual input snapshot. State the snapshot date, site (`mathoverflow.net` rather than `meta.mathoverflow.net`), preprocessing/edge extraction rule, and access date. Do not cite the Stack Exchange dump as if it were itself the published temporal-network dataset: the raw dump contains site tables, whereas the SNAP release defines the directed interaction files used for network analysis. If user-generated text or displayed posts are reproduced, separately follow the applicable Stack Exchange attribution requirements; the three sources above do not establish that the manuscript has satisfied page-level attribution for quoted content.

## Verification notes and limitations

- The SNAP page is a direct dataset record and explicitly links its source to the Stack Exchange Data Dump. Its page does not expose a DOI or a formal publication year, so the DOI field for [1] is intentionally empty.
- The Internet Archive item is a dated repository snapshot, not a peer-reviewed publication and not a DOI-bearing archival dataset. Its metadata says CC BY-SA 4.0, but licensing/attribution details can change with Stack Exchange’s dump process; retain the snapshot’s license file and cite the exact item used.
- The ACM record verifies [3] at the publisher. The paper is evidence for the published temporal-network source context, not evidence for the manuscript’s missingness design or ERGM/link-prediction claims.

## References

[1]: https://snap.stanford.edu/data/sx-mathoverflow.html "Math Overflow temporal network — SNAP dataset record"

[2]: https://archive.org/details/stack-exchange-data-dump-2023-03-08 "Stack Exchange Data Dump — 2023-03-08 — Internet Archive record"

[3]: https://doi.org/10.1145/3018661.3018731 "Motifs in Temporal Networks — ACM publisher record"
