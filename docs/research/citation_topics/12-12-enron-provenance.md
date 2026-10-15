# Citation topic: Enron email corpus provenance and methodological use

## Recommended sources

### [1] Official dataset record: Carnegie Mellon University Enron Email Dataset

**Bibliographic record.** William W. Cohen (maintainer), *Enron Email Dataset*, Carnegie Mellon University, CALO Project dataset page, current distribution identified on the page as the **May 7, 2015 version**. DOI: **none located** (official repository record; checked 2026-10-15). URL: <https://www.cs.cmu.edu/~enron/>.

**What it supports.** This is the authoritative provenance citation for the particular public corpus distribution: the page says the data were collected and prepared by the CALO Project; originated from material made public by the Federal Energy Regulatory Commission during its investigation; contain about 150 users (mostly senior management) and about 0.5 million messages; are organized into folders; exclude attachments; include redactions; and may contain normalized/placeholder addresses where invalid addresses could not be parsed. It also records that earlier distributions should be replaced by the May 7, 2015 distribution or corrected using the listed deletion file. These facts support a manuscript data paragraph that identifies Enron as a released, privacy- and integrity-processed email corpus and records the exact distribution/version used.

**Do not overclaim.** The page does **not** establish that every message is an authentic unaltered original, that the corpus is a random sample of Enron communication, or that an observed email edge is a complete organizational interaction. It also does not define a directed link-prediction target, an event-outcome convention, or an MCAR/MNAR missingness mechanism. The manuscript should therefore state its own event-to-edge construction and missingness design separately, and should report the downloaded version and any additional filtering.

### [2] Bryan Klimt and Yiming Yang (2004), “The Enron Corpus: A New Dataset for Email Classification Research”

**Bibliographic record.** Bryan Klimt and Yiming Yang. 2004. “The Enron Corpus: A New Dataset for Email Classification Research.” In *Machine Learning: ECML 2004*, Lecture Notes in Computer Science, vol. 3201, pp. 217–226. Springer, Berlin/Heidelberg. DOI: **10.1007/978-3-540-30115-8_22**. Publisher record: <https://link.springer.com/chapter/10.1007/978-3-540-30115-8_22>.

**What it supports.** The peer-reviewed ECML paper is the canonical original research citation for the corpus’s introduction as a benchmark/test bed. The publisher abstract states that the paper introduces the Enron corpus as a test bed for automated email-folder classification and information extraction from chronologically ordered email streams, and reports baseline support-vector-machine results under different email-field conditions. It supports wording such as “the Enron corpus was introduced as a public research test bed for email classification and ordered email-stream analysis.” It is useful background for why the corpus became methodologically important, while the official CMU record [1] should be used for the exact released distribution and cleaning/redaction details.

**Do not overclaim.** This paper is not a link-prediction study and does not validate directed network edges, ERGM scores, MPLE, missing-edge masks, or forecasting performance. Its classification baselines should not be described as a neural benchmark or as evidence for the manuscript’s network-prediction results.

### [3] Jana Diesner, Terrill L. Frantz, and Kathleen M. Carley (2005), “Communication Networks from the Enron Email Corpus ‘It’s Always About the People. Enron is no Different’”

**Bibliographic record.** Jana Diesner, Terrill L. Frantz, and Kathleen M. Carley. 2005. “Communication Networks from the Enron Email Corpus ‘It’s Always About the People. Enron is no Different’.” *Computational and Mathematical Organization Theory* 11: 201–228. Issue date 2005; publisher page records online publication 14 January 2006. DOI: **10.1007/s10588-005-5377-0**. Publisher record: <https://doi.org/10.1007/s10588-005-5377-0>.

**What it supports.** This is the most directly relevant peer-reviewed methodological precedent for using Enron email as an organizational communication network. The publisher abstract says the authors enhanced the original corpus database and analyzed the structure, properties, dynamics, and communicative behavior of an organizational communication network during crisis. It supports a narrowly framed claim that Enron has been used for social/dynamic network analysis of internal organizational communication and that the corpus can support temporal organizational-network diagnostics. It does **not** by itself support the manuscript’s particular directed local scores, static ERGM MPLE conditional-footprint scores, or 30 event-first MCAR/MNAR out-masks; those are the manuscript’s methods.

**Do not overclaim.** The article’s abstract describes network analysis and temporal/dynamic organizational communication, not link prediction, missingness robustness, MCMC-derived joint evidence, or full forecasting. Cite it only for the methodological precedent and the bounded temporal-network context.

## Recommended manuscript wording and citation discipline

Use [1] for corpus provenance, release/version, approximate scale, redaction and address-normalization caveats. Use [2] for the original research introduction of Enron as a classification/ordered-email-stream test bed. Use [3] for the peer-reviewed precedent that constructs/analyzes organizational communication networks from Enron email and motivates a bounded temporal diagnostic. None of these sources should be cited as evidence for neural benchmarking, MCMC-based joint L3 evidence, or full future-link forecasting.

The sources also imply an important reproducibility note: “the Enron corpus” is not a single immutable object. The CMU page distinguishes earlier releases and the May 7, 2015 distribution, and documents deletions/redactions and omitted attachments. The final manuscript should name the exact downloaded release, preserve the preprocessing/filtering rules, and distinguish native directed email events (sender to recipient, under the manuscript’s stated parsing rule) from any formal graph concept used for comparison.

## References

[1]: https://www.cs.cmu.edu/~enron/ "Enron Email Dataset — Carnegie Mellon University"

[2]: https://doi.org/10.1007/978-3-540-30115-8_22 "The Enron Corpus: A New Dataset for Email Classification Research"

[3]: https://doi.org/10.1007/s10588-005-5377-0 "Communication Networks from the Enron Email Corpus ‘It’s Always About the People. Enron is no Different’"

**Verification date:** 2026-10-15. Publisher metadata and abstracts were checked on SpringerLink/DOI landing pages; provenance and release notes were checked on the official CMU dataset page.