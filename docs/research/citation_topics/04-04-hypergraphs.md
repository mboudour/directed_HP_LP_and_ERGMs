# Citation topic: higher-order networks, directed hypergraphs, and hyperlink-prediction framing

## Recommended sources

### 1. Canonical directed-hypergraph formalism

**Giorgio Gallo, Giustino Longo, Stefano Pallottino, and Sang Nguyen (1993).** “Directed hypergraphs and applications.” *Discrete Applied Mathematics*, **42**(2–3), 177–201. DOI: [10.1016/0166-218X(93)90045-P](https://doi.org/10.1016/0166-218X(93)90045-P). Publisher record: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/0166218X9390045P). Cross-check: [Crossref record](https://api.crossref.org/works/10.1016%2F0166-218X%2893%2990045-P).

**What it supports in this manuscript:** Use this as the foundational citation when the manuscript distinguishes an ordinary directed dyad (one source and one target) from a directed hyperedge whose source and target incidence sets may contain multiple vertices. It supports treating directed hypergraphs as a formal generalization useful for modeling multi-entity directed relations, and it provides established directed-hypergraph concepts such as connectivity, paths, cuts, and applications in databases and related domains.

**Claim boundary:** The paper is a formal/mathematical treatment and does **not** validate the manuscript’s MCAR/MNAR masking design, Enron or MathOverflow analyses, ERGM MPLE scores, hyperlink-prediction accuracy, or temporal forecasting. Do not cite it as evidence that a particular email or forum dataset is a directed hypergraph.

### 2. Higher-order structure in directed networks

**Austin R. Benson, David F. Gleich, and Jure Leskovec (2016).** “Higher-order organization of complex networks.” *Science*, **353**(6295), 163–166. DOI: [10.1126/science.aad9029](https://doi.org/10.1126/science.aad9029). Publisher record: [Science](https://www.science.org/doi/10.1126/science.aad9029). Author manuscript/verification: [NIH PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5133458/).

**What it supports in this manuscript:** Use this source to motivate the narrow conceptual distinction between pairwise local link scores and higher-order organization represented by small subgraphs/motifs. The article explicitly includes all 13 connected three-node directed motifs in its framework and states that its higher-order clustering framework applies to directed, undirected, and weighted networks. This supports describing motif-based or higher-order structure as a formal concept relevant to directed network analysis, without re-labeling every dyadic prediction task as hyperlink prediction.

**Claim boundary:** Benson et al. study higher-order motif organization/clustering, not missing-hyperedge recovery. The paper does **not** support claims about hyperlink-prediction performance, missingness mechanisms, ERGMs, MPLE, or forecasting. Cite it only for the higher-order/motif conceptual background.

### 3. Hyperlink-prediction problem framing

**Can Chen and Yang-Yu Liu (2024).** “A survey on hyperlink prediction.” *IEEE Transactions on Neural Networks and Learning Systems*, **35**(11), 15034–15050. DOI: [10.1109/TNNLS.2023.3286280](https://doi.org/10.1109/TNNLS.2023.3286280). Publisher/author-manuscript verification: [NIH PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11584203/). IEEE record: [IEEE Xplore](https://ieeexplore.ieee.org/document/10163497/).

**What it supports in this manuscript:** Use this source for the terminology and task definition: hyperlink prediction is an extension of graph link prediction that infers missing hyperlinks in hypergraphs, where a hyperlink can connect more than two nodes. It also supports citing the broad methodological taxonomy (similarity-based, probability-based, matrix-optimization-based, and deep-learning-based approaches) if the manuscript needs to situate its non-neural local-score and static probability-model comparison.

**Claim boundary:** This is a survey, not an original estimator or a validation of the manuscript’s scores. Its benchmark includes deep-learning methods, but this manuscript must **not** claim a neural benchmark on that basis. The survey does not support claims about the manuscript’s 30 event-first MCAR/MNAR-out masks, Enron/MathOverflow results, ERGM MPLE conditional-footprint scores, MCMC-derived joint L3 evidence, or full forecasting. Use only its definition/taxonomy and explicitly state that the present study is a bounded, non-neural comparison.

## Scope note

Together these sources support a disciplined framing: directed hypergraphs provide the formal multi-source/multi-target object; higher-order motif work explains why directed subgraph structure is distinct from pairwise scores; and the hyperlink-prediction survey supplies the missing-hyperedge terminology. They do **not** imply that the manuscript’s native directed events are hyperedges. If the empirical data contain ordinary directed events, describe higher-order/hypergraph language as a formal comparison or framing device unless the event semantics genuinely encode multi-vertex tails and heads.

## Verification record

Bibliographic metadata were checked against the publisher pages and/or Crossref/NIH-hosted author manuscripts linked above. The three DOI strings are verified and should be retained exactly as shown (case-insensitive DOI resolution is acceptable).