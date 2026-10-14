# Ciel direction-semantics assessment

The available sources establish that Project Ciel is a 25-person, directed,
valued network reconstructed from police-wiretap communication data. They do
not establish the source-specific coding rule needed here: whether an entry at
row *i*, column *j* represents a contact initiated by *i* to *j* or the reverse.

The UCINET CielNet publisher describes ties as directed and valued communication
exchanges and gives Morselli's *Inside Criminal Networks* as the reconstruction
source, but does not define the row-to-column direction.[1] A recent study using
Project Ciel likewise calls its empirical networks directed communication
networks, but does not specify the orientation of the supplied Ciel matrix; it
then converts networks to undirected form for its intervention analysis.[2]

The primary book's accessible publisher preview identifies a section entitled
"The Direction of Contact," but the preview does not expose the relevant pages
or the Appendix matrix coding. The UCINET data-entry reference shows the
software's general labelled-matrix and ordered-pair formats, but it is not
source-specific evidence that the published `CIELNET.csv` rows encode callers.
It therefore cannot close this semantic gap.[3]

**Decision.** The Ciel direction gate remains **unapproved**. The matrix can be
retained and audited as a directed-valued source, but no directed arc, footprint,
formal-concept, or ERGM result will be constructed from it until a source that
explicitly maps the matrix row and column roles to the communication initiator
and recipient is located. This is a semantic safeguard, not a claim that the
network is undirected.

**References**

[1]: https://sites.google.com/site/ucinetsoftware/datasets/covert-networks/cielnet "Analytic Technologies CielNet documentation"
[2]: https://assets.pubpub.org/ccb6ab371-fc70-4ef3-b2e5-d0d0580b4d37/p0715ebe6-d410-4bf9-8f04-1b11137f2f86/exports/34d5624604c81126.pdf "Targeting Drug Trafficking Networks: A Comparative Evaluation of SNA-Informed Disruption Strategies"
[3]: http://www.analytictech.com/networks/dataentry.htm "Entering Data for Analysis by UCINET Software"
