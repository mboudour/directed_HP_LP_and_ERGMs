# Citation topic: foundational link prediction, local structural scores, and ranking evaluation

## Recommended sources

### [1] Liben-Nowell & Kleinberg (2007)

**Bibliographic record:** David Liben-Nowell and Jon Kleinberg. 2007. “The link-prediction problem for social networks.” *Journal of the American Society for Information Science and Technology* 58(7): 1019–1031. DOI: [10.1002/asi.20591](https://doi.org/10.1002/asi.20591). Publisher record: [Wiley Online Library](https://asistdl.onlinelibrary.wiley.com/doi/abs/10.1002/asi.20591).

**What it supports.** This is the foundational citation for framing link prediction from an observed network snapshot: infer which currently absent node pairs will interact later, and score candidate pairs from network proximity/topological information. The publisher abstract explicitly defines the problem, describes proximity-based approaches, and reports experiments showing that future interactions can be extracted from topology alone and that subtler proximity measures can outperform direct measures. It can therefore support the manuscript’s general introduction to link prediction and its bounded temporal diagnostic.

**Claim boundary.** The paper studies social-network link prediction primarily in coauthorship networks and does not establish the manuscript’s directed event-first MCAR/MNAR-out masking design, static ERGM MPLE conditional-footprint scores, or any claim of full forecasting. It should not be cited as evidence for neural benchmarks, MCMC-derived joint L3 evidence, or a directed-specific method.

### [2] Adamic & Adar (2003)

**Bibliographic record:** Lada A. Adamic and Eytan Adar. 2003. “Friends and neighbors on the Web.” *Social Networks* 25(3): 211–230. DOI: [10.1016/S0378-8733(03)00009-1](https://doi.org/10.1016/S0378-8733(03)00009-1). Publisher record: [Elsevier ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378873303000091).

**What it supports.** This original peer-reviewed study supports the use of local structural/content indicators as predictors of social connections, including the intuition behind shared-neighbor-style similarity and the Adamic–Adar family of local scores. Its abstract says the authors devise techniques to mine Web/homepage information, compare indicators of social connections across Stanford and MIT data, and evaluate prediction schemes for link structures. It is appropriate when the manuscript introduces local proximity scores as formal structural concepts and distinguishes them from native directed events.

**Claim boundary.** The study concerns homepage/social connections and combines link structure with information such as shared terms and mailing lists; it is not a validation of every directed score, of orientation-sensitive source→target prediction, or of the manuscript’s Enron/MathOverflow missingness masks. Do not use it to claim that Adamic–Adar is inherently directed, that its original study used ERGMs, or that it supports MNAR identification or temporal forecasting.

### [3] Saito & Rehmsmeier (2015)

**Bibliographic record:** Takaya Saito and Marc Rehmsmeier. 2015. “The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets.” *PLOS ONE* 10(3): e0118432. DOI: [10.1371/journal.pone.0118432](https://doi.org/10.1371/journal.pone.0118432). Official article record: [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432).

**What it supports.** This peer-reviewed paper supports the manuscript’s ranking-evaluation rationale when candidate dyads are highly imbalanced: precision–recall (PR) displays the fraction of true positives among positive predictions, and PR plots can be more informative than ROC plots for judging performance under strong class imbalance. It can justify reporting PR-based ranking diagnostics (with the manuscript’s exact metric definition stated separately) rather than treating ROC summaries as sufficient.

**Claim boundary.** The paper evaluates binary classifiers and PR/ROC visualization; it does not define link-prediction scores, directed network semantics, missingness mechanisms, ERGM estimation, or a particular top-k/average-precision protocol. It therefore supports the imbalance/evaluation principle only, not a claim that any one score or model is superior on Enron or MathOverflow.

## Scope and citation-use note

Together these sources cover (i) the foundational snapshot-to-future link-prediction formulation, (ii) original local proximity/structural indicators, and (iii) evaluation under the extreme positive–negative imbalance typical of candidate-dyad ranking. They do **not** support claims about neural baselines, MCMC-derived joint L3 evidence, full forecasting, ERGM MPLE conditional footprints, or the validity of the manuscript’s 30 event-first MCAR and MNAR-out masks. Those claims require separate methodological or dataset citations and should not be attributed to the three sources above.

## Verification record

Metadata and abstracts were checked against the publisher records linked above. Wiley lists the Liben-Nowell–Kleinberg article as first published 26 March 2007, volume 58 issue 7, pages 1019–1031, and DOI 10.1002/asi.20591. Elsevier lists Adamic–Adar as *Social Networks* volume 25 issue 3, July 2003, pages 211–230, and DOI 10.1016/S0378-8733(03)00009-1. PLOS lists Saito–Rehmsmeier as published 4 March 2015, *PLOS ONE* 10(3), e0118432, and DOI 10.1371/journal.pone.0118432.
