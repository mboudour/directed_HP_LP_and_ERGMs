# Citation topic: paired bootstrap and randomization/permutation inference for repeated matched evaluations

**Scope.** These sources support inference for *paired/matched repeated evaluations*: compare two methods on the same evaluation units (here, the same event-first MCAR/MNAR mask and held-out candidate set), compute a paired difference per unit, and resample or randomize while preserving that pairing. They do **not** justify claims about neural benchmarks, MCMC-derived joint L3 evidence, or full temporal forecasting.

## Recommended sources

### 1. Berg-Kirkpatrick, Burkett, and Klein (2012)

**Citation.** Taylor Berg-Kirkpatrick, David Burkett, and Dan Klein. 2012. “An Empirical Investigation of Statistical Significance in NLP.” *Proceedings of the 2012 Joint Conference on Empirical Methods in Natural Language Processing and Computational Natural Language Learning*, 995–1005. Association for Computational Linguistics. DOI: **none listed in the official ACL Anthology record**. Official record and PDF: <https://aclanthology.org/D12-1091/>.

**What it supports.** This is the closest methodological precedent for the manuscript’s repeated matched score comparisons. The paper explicitly frames system comparison on the same test set, uses a **paired bootstrap**, gives an algorithm that resamples evaluation items with replacement while retaining both systems’ outputs for each sampled item, and explains recentering the bootstrap difference under the null. It also states that the paired bootstrap can be applied to complex performance metrics. These points support reporting paired bootstrap uncertainty/significance for score differences across matched event-level evaluations, provided the manuscript defines the resampling unit and preserves each method’s paired outcome within that unit.

**What it does not support.** It is an NLP evaluation study, not a network-link-prediction paper; it does not validate the manuscript’s particular MCAR/MNAR masks, ERGM MPLE scores, directed-network estimands, or any claim of temporal forecasting. Its discussion of approximate randomization is a methodological contrast and says that method is not appropriate for the specific null hypothesis used in that paper, so it should not be cited as evidence that permutation is universally preferable.

### 2. Riezler and Maxwell (2005)

**Citation.** Stefan Riezler and John T. Maxwell. 2005. “On Some Pitfalls in Automatic Evaluation and Significance Testing for MT.” *Proceedings of the ACL Workshop on Intrinsic and Extrinsic Evaluation Measures for Machine Translation and/or Summarization*, 57–64. Association for Computational Linguistics. DOI: **none listed in the official ACL Anthology record**. Official record and PDF: <https://aclanthology.org/W05-0908/>.

**What it supports.** This source is the best direct citation for the **matched-evaluation randomization/permutation side** of the topic. It examines statistical significance when comparing systems evaluated on the same items and discusses approximate randomization alongside bootstrap-based testing, including the dependence of test behavior on the evaluation metric and the null being tested. It supports stating that a paired randomization/permutation test is a legitimate nonparametric option for repeated matched method comparisons when the randomization scheme is explicitly defined (for example, swapping method labels within matched evaluation units under a sharp exchangeability null).

**What it does not support.** It does not establish validity for arbitrary network masks or dependence structures, and it does not justify treating the 30 masks as independent observations without qualification. The manuscript should distinguish randomization over paired method labels/within-unit outcomes from resampling masks, and should state which null and exchangeability assumptions are used.

### 3. Efron and Tibshirani (1994 [copyright 1993])

**Citation.** Bradley Efron and R. J. Tibshirani. 1994. *An Introduction to the Bootstrap*. 1st ed. Chapman and Hall/CRC. DOI: **10.1201/9780429246593**. Publisher record: <https://www.taylorfrancis.com/books/mono/10.1201/9780429246593/introduction-bootstrap-bradley-efron-tibshirani>.

**What it supports.** This canonical book supports the general statistical description of the bootstrap as a computer-based method for approximating sampling distributions and assessing variance, bias, coverage, and related uncertainty. It is appropriate for defining paired bootstrap resampling and for justifying confidence intervals or Monte Carlo estimates derived from repeated resamples, while the paired-evaluation papers above supply the application-specific precedent.

**What it does not support.** The book alone does not specify the manuscript’s graph-dependent resampling unit, missingness mechanism, mask-generation design, or a particular hypothesis test. It should not be used to claim that bootstrap intervals automatically account for dependence among masks, events, nodes, or candidate links.

## Verification notes

The bibliographic metadata above was checked against official publisher or repository records. The ACL Anthology records identify authors, year, venue, pages, publisher, and stable URLs for the Berg-Kirkpatrick et al. and Riezler–Maxwell papers; neither record supplies a DOI, so the DOI field is intentionally empty rather than inferred. Taylor & Francis supplies the Efron–Tibshirani authors, first-publication/eBook year, edition, publisher/imprint, and DOI.

For this manuscript, the defensible claim is narrow: **paired bootstrap and/or paired randomization inference can quantify uncertainty or test differences between directed link-prediction and static ERGM-MPLE conditional-footprint scores when each replicate/mask produces matched outcomes and the resampling/randomization unit and null are stated.** The cited sources do not authorize broader claims about neural baselines, joint MCMC L3 evidence, or full forecasting.
