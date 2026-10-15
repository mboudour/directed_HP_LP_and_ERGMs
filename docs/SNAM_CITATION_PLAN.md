# SNAM Directed-Missingness Manuscript — Citation Plan

## Decision summary

**Selected sources: 23** — **16 indispensable** and **7 optional context/caveat sources**. This is a deliberately small, non-redundant bibliography for a **static, directed, missingness-centred** manuscript. It supports (i) a design-based missingness stress test, (ii) static directed link scoring and ranking evaluation, (iii) an explicitly conditional static-ERGM/MPLE interpretation, (iv) matched-evaluation uncertainty, and (v) dataset provenance.

> **Scope guardrail.** The manuscript must describe its MCAR and MNAR-out masks as *assumption-indexed, event-first design-based stress tests*, not as empirical identification of either corpus's real observation mechanism. A static ERGM MPLE score is a **dyad-conditional footprint**, not a joint-network probability, a temporal hazard, or evidence from MCMC. The study makes **no neural-baseline comparison**, **no MCMC-derived joint L3 claim**, and **no full forecasting claim**. No citation below should be used to imply otherwise.

The selected sources are arranged by the section in which they should first be cited. A source marked **Optional** enters the BibTeX file only if the indicated sentence, method feature, or caveat remains in the final manuscript.

## Citation rules to apply throughout

1. **Use precise evidentiary verbs.** Say “we define,” “we construct,” “we evaluate under,” or “we use as a stress test” for manuscript choices. Reserve “following” or “as formalized by” for the limited concepts actually supplied by the cited source.
2. **Do not call the data’s missingness MCAR, MAR, or MNAR.** These labels characterize the *simulated mask rule* conditional on an explicitly stated observation model. In particular, “MNAR-out” is manuscript shorthand for an edge/outcome-dependent removal design; it is not evidence that Enron or MathOverflow is empirically MNAR.
3. **Keep time out of performance claims.** If a chronological split is retained, call it a *bounded chronological diagnostic*, state its horizon and snapshot/event aggregation choices, and do not label it forecasting. The current static manuscript does not require temporal-ERGM, relational-event, point-process, or relational-hyperevent method citations.
4. **Keep model interpretations separate.** A change-statistic logit is conditional on the remainder of a static graph. An MPLE is a pseudolikelihood-based estimator. Neither provides joint evidence for any L3 object.
5. **Cite each dataset at release level.** Record the exact downloaded release/file set, download date, checksums where available, filtering/aggregation, duplicate handling, self-loop policy, actor universe, and time window in the reproducibility appendix. Do not merge static and temporal SNAP releases or their node identifiers.

## Planned manuscript sections

### 1. Introduction and scope: missingness as a network-measurement sensitivity problem

| Priority | Citation placement and permissible claim | Sources |
|---|---|---|
| **Indispensable** | First paragraph defining MCAR/MAR/MNAR terminology and why ignoring an observation process needs assumptions. State immediately that the manuscript **does not identify** the real mechanism. | Rubin (1976) |
| **Indispensable** | Motivation that actor/tie omission, boundary specification, non-response, and degree-censoring can alter network statistics. Use to motivate sensitivity analysis, **not** to validate this manuscript’s masks or results. | Kossinets (2006) |
| **Optional** | Add only if the methods section explicitly contrasts random deletion with edge/outcome-dependent deletion in directed as well as undirected graph simulations. Use as corroborating network-imputation context, not formal mechanism proof. | Huisman (2009) |

**Recommended text logic.** Define the simulation rule first; then say that the analysis studies robustness *under those rules*. Do not write “we model the Enron/MathOverflow missing-data mechanism” unless an actual observation model is added and separately justified.

### 2. Data and static event-to-dyad construction

| Priority | Citation placement and permissible claim | Sources |
|---|---|---|
| **Indispensable** | Enron provenance/release paragraph: public FERC-origin material prepared through CALO; release-specific caveats including redaction, omitted attachments, and corrections. Name the exact CMU release used. | Cohen / CMU Enron dataset record (2015) |
| **Optional** | One sentence establishing only that Enron email has previously been enhanced and examined as an organizational communication network. Do not cite it for the present sender–recipient convention or masking method. | Diesner, Frantz & Carley (2005/2006) |
| **Indispensable** | MathOverflow provenance paragraph: derived SNAP answer/comment interactions, directed timestamped `SRC DST UNIXTS` records, and OwnerUserId mapping. State the exact component/union file and preprocessing used. | Stanford SNAP MathOverflow record (n.d.) |
| **Indispensable** | Scholarly companion citation for the published temporal-network release context named by SNAP. This supports provenance/context, not the present link-prediction, missingness, or ERGM results. | Paranjape, Benson & Leskovec (2017) |

**Required manuscript disclosure.** The source corpora do not dictate a single canonical static adjacency construction. Explicitly state the event-to-dyad aggregation rule, observation interval, treatment of repeated events, and whether each static directed tie means “at least one retained event.” Do not assert that either dataset consists of directed hyperedges unless the analysis actually represents multi-recipient events as source and receiver-set relations.

### 3. Static directed local scores and ranking evaluation

| Priority | Citation placement and permissible claim | Sources |
|---|---|---|
| **Indispensable** | Link-prediction framing: score candidate ties using topology/proximity and evaluate a withheld tie set. If a chronological check remains, describe it as a bounded diagnostic rather than a full forecasting study. | Liben-Nowell & Kleinberg (2007) |
| **Indispensable** | Directed-score methods paragraph: common-neighbor-style indices require directional modification; path-based indices must respect edge direction. | Lü & Zhou (2011) |
| **Optional** | Cite only beside a specifically implemented/illustrated directed bi-fan ingredient. Present it as a model-specific directed motif, never as a universal closure rule. | Zhang *et al.* (2013) |
| **Optional** | Cite only if the manuscript introduces or interprets orientation-specific closure terminology, in-/out-degree asymmetry, or multiple labeled directed wedges. It is terminology/context, not validation of the scores. | Yin, Benson & Ugander (2020) |
| **Indispensable** | Evaluation paragraph: justify precision–recall/ranking diagnostics in a severely imbalanced candidate space. Do not attribute an exact top-*k* or AP protocol to this paper unless its protocol is independently specified. | Saito & Rehmsmeier (2015) |

**Do not add an undirected shared-neighbor historical citation by default.** Adamic and Adar (2003) is sound background, but is redundant here because the manuscript’s actual methodological issue is directionality, directly covered by Lü and Zhou (2011). Add it only if a named Adamic–Adar score is actually reported.

### 4. Formal-concept / maximal-biclique component (conditional section)

Include this section **only if** the final manuscript retains an FCA construction. State before the formal definitions that mapping directed-network entities to an object–attribute incidence context is the manuscript’s modeling choice; a formal concept is not a native directed event.

| Priority | Citation placement and permissible claim | Sources |
|---|---|---|
| **Indispensable when this section exists** | Definitions of formal context, derivation/Galois operators, closure, formal concepts, and concept lattice. | Ganter & Wille (1999) |
| **Optional** | One graph-theoretic bridge: under the explicitly defined binary incidence mapping, closed extent–intent pairs correspond to maximal all-ones rectangles / maximal bicliques. | Zhang *et al.* (2014) |

**Prohibited inference.** Neither source is evidence for predictive superiority, neural comparisons, MCMC joint evidence, ERGM estimation, corpus-specific findings, or any missingness claim.

### 5. Static directed ERGM conditional-footprint methods

| Priority | Citation placement and permissible claim | Sources |
|---|---|---|
| **Indispensable** | Brief historical/foundational opening for the exponential-family / Markov-graph (p*) perspective and local-logit interpretation. | Wasserman & Pattison (1996) |
| **Indispensable** | Equation defining a dyad change statistic and the static conditional tie probability: inverse-logit of natural parameters dotted with change statistics, conditional on the rest of the graph. | Krivitsky, Handcock & Morris (2011) |
| **Indispensable** | Estimation/interpretation paragraph: MPLE is formed from local conditional terms and differs from full likelihood under edge dependence. Use this to label the output a **conditional footprint**, never a joint score. | van Duijn, Gile & Handcock (2009) |
| **Indispensable** | Specification paragraph for geometrically weighted degree, alternating *k*-triangle, and alternating independent two-path statistics in graphs and digraphs. | Snijders, Pattison, Robins & Handcock (2006) |
| **Indispensable** | Definition/interpretation of directed structural terms: cyclic, shared-choice/activity, and shared-popularity closure; in-/out-degree roles; and reciprocity as directed mutuality. Do not collapse all directed triangles into one statistic. | Robins, Pattison & Wang (2009) |
| **Optional** | A narrowly worded stability caveat: instability/near-degeneracy can make simulation and inference difficult. Do not assert that the fitted models are degenerate without diagnostics. | Schweinberger (2012) |

**Required notation discipline.** Define all directed ERGM terms in the manuscript rather than relying on a generic “triangle” label. State that the score is computed from the observed/retained static graph under the specified fit; do not call it a temporal hazard, posterior predictive probability, or a joint-network likelihood.

### 6. Matched repeated-mask uncertainty and comparison

| Priority | Citation placement and permissible claim | Sources |
|---|---|---|
| **Indispensable** | General bootstrap rationale for approximating a sampling distribution, uncertainty, bias, and coverage. | Efron & Tibshirani (1994) |
| **Indispensable** | Matched-evaluation precedent: resample/evaluate paired systems on the same units and use a paired bootstrap appropriate to complex metrics. The manuscript must identify the resampling unit. | Berg-Kirkpatrick, Burkett & Klein (2012) |
| **Optional** | If a paired randomization/permutation test is actually used, specify the within-unit exchangeability rule and sharp null. Cite this as a warning about metric/null dependence, not proof that arbitrary graph-dependent permutations are valid. | Riezler & Maxwell (2005) |

**Required inferential caveat.** The 30 masks are repeated matched experimental conditions, **not 30 independent networks**. Report effect estimates and uncertainty at the explicitly stated event/dyad/mask resampling level, and acknowledge graph dependence and the conditional nature of the resampling interpretation.

## Selected-source bibliography records and verification links

These are the complete metadata records to carry into the bibliography once the checks in the next section are completed. Direct links are retained both for verification and for data/software-style citations.

### Indispensable sources (16)

1. **Rubin, Donald B. (1976).** “Inference and Missing Data.” *Biometrika* **63**(3), 581–592. DOI: [10.1093/biomet/63.3.581](https://doi.org/10.1093/biomet/63.3.581). Source type: original peer-reviewed statistical article. Verification URL: <https://doi.org/10.1093/biomet/63.3.581>.

2. **Kossinets, Gueorgi (2006).** “Effects of Missing Data in Social Networks.” *Social Networks* **28**(3), 247–268. DOI: [10.1016/j.socnet.2005.07.002](https://doi.org/10.1016/j.socnet.2005.07.002). Source type: original peer-reviewed network article. Verification URL: <https://www.sciencedirect.com/science/article/abs/pii/S0378873305000511>.

3. **Cohen, William W. (maintainer) (2015).** *Enron Email Dataset*. Carnegie Mellon University / CALO Project official dataset record. DOI: none assigned. Source type: official dataset repository record. Verification URL: <https://www.cs.cmu.edu/~enron/>. Use the release date/version actually downloaded in the final bibliography.

4. **Stanford Network Analysis Project (SNAP) (n.d.).** *Math Overflow temporal network*. SNAP Network Data Sets, Stanford University. DOI: none assigned. Source type: official dataset repository record. Verification URL: <https://snap.stanford.edu/data/sx-mathoverflow.html>.

5. **Paranjape, Ashwin, Austin R. Benson, and Jure Leskovec (2017).** “Motifs in Temporal Networks.” In *Proceedings of the Tenth ACM International Conference on Web Search and Data Mining (WSDM ’17)*, 601–610. DOI: [10.1145/3018661.3018731](https://doi.org/10.1145/3018661.3018731). Source type: original peer-reviewed conference paper. Verification URL: <https://dl.acm.org/doi/10.1145/3018661.3018731>.

6. **Liben-Nowell, David, and Jon Kleinberg (2007).** “The Link-Prediction Problem for Social Networks.” *Journal of the American Society for Information Science and Technology* **58**(7), 1019–1031. DOI: [10.1002/asi.20591](https://doi.org/10.1002/asi.20591). Source type: original peer-reviewed journal article. Verification URL: <https://asistdl.onlinelibrary.wiley.com/doi/abs/10.1002/asi.20591>.

7. **Lü, Linyuan, and Tao Zhou (2011).** “Link Prediction in Complex Networks: A Survey.” *Physica A: Statistical Mechanics and its Applications* **390**(6), 1150–1170. DOI: [10.1016/j.physa.2010.11.027](https://doi.org/10.1016/j.physa.2010.11.027). Source type: peer-reviewed review/minireview. Verification URL: <https://www.sciencedirect.com/science/article/abs/pii/S037843711000991X>.

8. **Saito, Takaya, and Marc Rehmsmeier (2015).** “The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets.” *PLOS ONE* **10**(3), e0118432. DOI: [10.1371/journal.pone.0118432](https://doi.org/10.1371/journal.pone.0118432). Source type: original peer-reviewed journal article. Verification URL: <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432>.

9. **Ganter, Bernhard, and Rudolf Wille (1999).** *Formal Concept Analysis: Mathematical Foundations*. Springer-Verlag, Berlin Heidelberg. DOI: [10.1007/978-3-642-59830-2](https://doi.org/10.1007/978-3-642-59830-2). Source type: canonical scholarly textbook. Verification URL: <https://link.springer.com/book/10.1007/978-3-642-59830-2>.

10. **Wasserman, Stanley, and Philippa Pattison (1996).** “Logit Models and Logistic Regressions for Social Networks: I. An Introduction to Markov Graphs and p*.” *Psychometrika* **61**, 401–425. DOI: [10.1007/BF02294547](https://doi.org/10.1007/BF02294547). Source type: foundational peer-reviewed journal article. Verification URL: <https://link.springer.com/article/10.1007/BF02294547>.

11. **Krivitsky, Pavel N., Mark S. Handcock, and Martina Morris (2011).** “Adjusting for Network Size and Composition Effects in Exponential-Family Random Graph Models.” *Statistical Methodology* **8**(4), 319–339. DOI: [10.1016/j.stamet.2011.01.005](https://doi.org/10.1016/j.stamet.2011.01.005). Source type: peer-reviewed journal article. Verification URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC3117581/>.

12. **van Duijn, Marijtje A. J., Krista J. Gile, and Mark S. Handcock (2009).** “A Framework for the Comparison of Maximum Pseudo Likelihood and Maximum Likelihood Estimation of Exponential Family Random Graph Models.” *Social Networks* **31**(1), 52–62. DOI: [10.1016/j.socnet.2008.10.003](https://doi.org/10.1016/j.socnet.2008.10.003). Source type: original peer-reviewed article. Verification URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC3500576/>.

13. **Snijders, Tom A. B., Philippa E. Pattison, Garry L. Robins, and Mark S. Handcock (2006).** “New Specifications for Exponential Random Graph Models.” *Sociological Methodology* **36**(1), 99–153. DOI: [10.1111/j.1467-9531.2006.00176.x](https://doi.org/10.1111/j.1467-9531.2006.00176.x). Source type: original peer-reviewed journal article. Verification URL: <https://onlinelibrary.wiley.com/doi/10.1111/j.1467-9531.2006.00176.x>.

14. **Robins, Garry, Pip Pattison, and Peng Wang (2009).** “Closure, Connectivity and Degree Distributions: Exponential Random Graph (p*) Models for Directed Social Networks.” *Social Networks* **31**(2), 105–117. DOI: [10.1016/j.socnet.2008.10.006](https://doi.org/10.1016/j.socnet.2008.10.006). Source type: original peer-reviewed journal article. Verification URL: <https://www.sciencedirect.com/science/article/abs/pii/S0378873308000592>.

15. **Efron, Bradley, and R. J. Tibshirani (1994).** *An Introduction to the Bootstrap*, 1st ed. Chapman and Hall/CRC. DOI: [10.1201/9780429246593](https://doi.org/10.1201/9780429246593). Source type: canonical statistical book. Verification URL: <https://www.taylorfrancis.com/books/mono/10.1201/9780429246593/introduction-bootstrap-bradley-efron-tibshirani>.

16. **Berg-Kirkpatrick, Taylor, David Burkett, and Dan Klein (2012).** “An Empirical Investigation of Statistical Significance in NLP.” In *Proceedings of the 2012 Joint Conference on Empirical Methods in Natural Language Processing and Computational Natural Language Learning*, 995–1005. Association for Computational Linguistics. DOI: none assigned in the official record. Source type: peer-reviewed conference paper. Verification URL: <https://aclanthology.org/D12-1091/>.

### Optional context/caveat sources (7)

17. **Huisman, Mark (2009).** “Imputation of Missing Network Data: Some Simple Procedures.” *Journal of Social Structure* **10**(1), 1–29. DOI: none found in the checked official records/Crossref; verify before final BibTeX entry. Source type: peer-reviewed network article. Verification URL: <https://research.rug.nl/en/publications/imputation-of-missing-network-data-some-simple-procedures/>.

18. **Diesner, Jana, Terrill L. Frantz, and Kathleen M. Carley (2005; issue year, online publication 2006).** “Communication Networks from the Enron Email Corpus ‘It’s Always About the People. Enron is no Different’.” *Computational and Mathematical Organization Theory* **11**, 201–228. DOI: [10.1007/s10588-005-5377-0](https://doi.org/10.1007/s10588-005-5377-0). Source type: original peer-reviewed journal article. Verification URL: <https://doi.org/10.1007/s10588-005-5377-0>.

19. **Zhang, Qian-Ming, Linyuan Lü, Wen-Qiang Wang, Yu-Xiao Zhu, and Tao Zhou (2013).** “Potential Theory for Directed Networks.” *PLOS ONE* **8**(2), e55437. DOI: [10.1371/journal.pone.0055437](https://doi.org/10.1371/journal.pone.0055437). Source type: peer-reviewed original research article. Verification URL: <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0055437>.

20. **Yin, Hao, Austin R. Benson, and Johan Ugander (2020).** “Measuring Directed Triadic Closure with Closure Coefficients.” *Network Science* **8**(4), 551–573. DOI: [10.1017/nws.2020.20](https://doi.org/10.1017/nws.2020.20). Source type: peer-reviewed original research article. Verification URL: <https://www.cambridge.org/core/journals/network-science/article/measuring-directed-triadic-closure-with-closure-coefficients/AC84C4CF8198E97DE659FED95F64859D>.

21. **Zhang, Yun, Charles A. Phillips, Gary L. Rogers, Erich J. Baker, Elissa J. Chesler, and Michael A. Langston (2014).** “On Finding Bicliques in Bipartite Graphs: A Novel Algorithm and Its Application to the Integration of Diverse Biological Data Types.” *BMC Bioinformatics* **15**, 110. DOI: [10.1186/1471-2105-15-110](https://doi.org/10.1186/1471-2105-15-110). Source type: peer-reviewed journal article. Verification URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC4038116/>.

22. **Schweinberger, Michael (2012).** “Instability, Sensitivity, and Degeneracy of Discrete Exponential Families.” *Journal of the American Statistical Association* **106**(496), 1361–1370. DOI: [10.1198/jasa.2011.tm10747](https://doi.org/10.1198/jasa.2011.tm10747). Source type: original peer-reviewed article. Verification URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC3405854/>.

23. **Riezler, Stefan, and John T. Maxwell (2005).** “On Some Pitfalls in Automatic Evaluation and Significance Testing for MT.” In *Proceedings of the ACL Workshop on Intrinsic and Extrinsic Evaluation Measures for Machine Translation and/or Summarization*, 57–64. Association for Computational Linguistics. DOI: none assigned in the official record. Source type: peer-reviewed workshop paper. Verification URL: <https://aclanthology.org/W05-0908/>.

## Final metadata checks before BibTeX freeze

Perform these checks after the exact data downloads and final method choices are frozen. These are the only unresolved metadata issues in the selected set.

| Source | What is incomplete or ambiguous | Required final action |
|---|---|---|
| **Huisman (2009)** | No DOI was found in the checked official Journal of Social Structure, University of Groningen, or Crossref records. | Confirm that no DOI exists; preserve the journal volume/issue/pages and use the official record/PDF URL rather than inventing a DOI. Omit entirely if the optional directed missing-data sentence is dropped. |
| **Berg-Kirkpatrick, Burkett & Klein (2012)** | The official ACL record lists no DOI. | Confirm ACL Anthology ID `D12-1091`, proceedings title, page range, and that DOI remains blank/not assigned; do not fabricate one. |
| **Riezler & Maxwell (2005)** | The official ACL record lists no DOI. | Confirm ACL Anthology ID `W05-0908`, workshop title, page range, and that DOI remains blank/not assigned. Omit entirely if the optional randomization test is not used. |
| **Cohen / CMU Enron record** | Dataset/web citation needs the exact release/distribution actually downloaded; the repository page documents a May 7, 2015 distribution but an analysis may use a different local copy. | Record release name/date, retrieval date, source URL, archive checksum/file inventory, and the maintained-by attribution as it appears in the actual release. |
| **SNAP MathOverflow record** | Corporate author/date is `Stanford Network Analysis Project (SNAP), n.d.` and the final analysis may use a particular union/component file or an archived snapshot. | Record exact file(s), snapshot/version if shown, retrieval date, and file checksum. Keep DOI blank unless the record later assigns one; cite Paranjape *et al.* separately for the published companion paper. |
| **Diesner, Frantz & Carley** | Issue year is 2005 while online-publication information is 2006. | Check publisher metadata and choose the bibliography year required by the target style (normally issue year 2005); do not list conflicting years in a single BibTeX `year` field. Omit if the optional Enron-network-precedent sentence is removed. |

## Excluded sources and why they should not enter the current bibliography

The following verified topics were deliberately **not selected**, so the manuscript cannot accidentally broaden its claims:

- **Temporal ERGM / btergm:** Hanneke, Fu & Xing (2010) and Leifeld, Cranmer & Desmarais (2018) are excluded because the agreed contribution is static and missingness-centred; no full temporal model or forecasting evaluation is claimed.
- **Relational-event, point-process, and hyperevent forecasting context:** Butts (2008), Perry & Wolfe (2013), and Lerner & Lomi (2023) are excluded. Dataset event records are described directly from the release documentation, without converting the methods paper into evidence of temporal modeling.
- **Directed hypergraphs and hyperlink prediction:** Gallo *et al.* (1993), Benson, Gleich & Leskovec (2016), and Chen & Liu (2024) are excluded. The present representation is directed dyadic events aggregated to static ties; no directed-hyperedge or neural hyperlink-prediction analysis is performed.
- **Additional FCA history:** Wille (1982) is excluded as redundant with Ganter & Wille (1999) for the needed definitions.
- **MCMC estimation:** Snijders (2002) is excluded because no MCMC estimation, simulated joint-network evidence, or MCMC-derived L3 result is reported.
- **Older directed-ERGM foundation:** Holland & Leinhardt (1981) is excluded as historical overlap with the selected static ERGM foundation and the more directly useful directed-term source.
- **Undirected local-score origin:** Adamic & Adar (2003) is excluded unless the exact named score is reported; the selected directed review is the better fit for the present directional methods.
- **email-Eu-core sources:** the SNAP email-Eu-core temporal/static records and the associated Paranjape *et al.* dataset context are excluded unless email-Eu-core becomes an analyzed corpus. They do not provide Enron or MathOverflow provenance, and static/temporal releases must not be treated as interchangeable.
- **Raw Stack Exchange archive snapshot:** the Internet Archive `Stack Exchange Data Dump - 2023-03-08` record is excluded unless that exact raw snapshot was actually used or audited. SNAP is the primary citation for the derived `sx-mathoverflow` edge semantics.

## Pre-submission citation audit

Before submission, verify all of the following:

- [ ] Every MCAR/MNAR-out occurrence says **mask/stress-test design**, not a discovered property of the corpus.
- [ ] Every static ERGM score is described as conditional; no wording implies a joint probability or MCMC evidence.
- [ ] No abstract, table, or caption claims neural-baseline comparison, full forecasting, or predictive superiority beyond the actual matched static evaluations.
- [ ] All directed closure terms are named separately and operationally defined.
- [ ] Enron and MathOverflow entries name their exact release/files and preprocessing decisions.
- [ ] Every optional source still has a live, claim-matched citation; otherwise remove it from both the manuscript and BibTeX.
- [ ] All six metadata items in the preceding table are resolved or omitted before BibTeX freeze.
