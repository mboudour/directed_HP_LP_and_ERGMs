# Citation topic: directed-network link prediction and directed local structure

## Scope

These sources support the manuscript's treatment of **native directed local link-prediction scores** and directed local structure under missingness. They do not support claims about neural-network benchmarks, MCMC-derived joint L3 evidence, or full temporal forecasting.

## Recommended sources

### 1. Lü and Zhou (2011)

- **Authors:** Linyuan Lü and Tao Zhou
- **Year:** 2011
- **Title:** “Link prediction in complex networks: A survey”
- **Venue:** *Physica A: Statistical Mechanics and its Applications* 390(6), 1150–1170
- **DOI:** [10.1016/j.physa.2010.11.027](https://doi.org/10.1016/j.physa.2010.11.027)
- **Publisher record:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S037843711000991X)
- **Source type:** Peer-reviewed review/minireview
- **What it supports:** The manuscript can cite this survey for the standard link-prediction framing—ranking unobserved node pairs using structural information—and for the taxonomy of local, global, and quasi-local similarity indices. Crucially for this topic, its directed-networks discussion states that ordinary undirected common-neighbor indices must be modified to account for directed local motifs, and that path-based indices must incorporate edge direction. This supports presenting directed scores as direction-aware local structural rules rather than silently applying undirected formulas.
- **Claim boundary:** This is a survey, not an original directed-score proposal. It should not be cited as evidence for a particular Enron or MathOverflow result, an MCAR/MNAR design, or a temporal-forecasting claim.

### 2. Zhang et al. (2013)

- **Authors:** Qian-Ming Zhang, Linyuan Lü, Wen-Qiang Wang, Yu-Xiao Zhu, and Tao Zhou
- **Year:** 2013
- **Title:** “Potential Theory for Directed Networks”
- **Venue:** *PLOS ONE* 8(2), e55437
- **DOI:** [10.1371/journal.pone.0055437](https://doi.org/10.1371/journal.pone.0055437)
- **Publisher record:** [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0055437)
- **Source type:** Peer-reviewed original research article
- **What it supports:** This is a direct precedent for a **native directed** local predictor. The paper proposes potential theory for directed networks, derives the four-node directed bi-fan as a preferred local structure under its mechanism, and constructs a corresponding bi-fan predictor for missing directed links. It supports describing directed local motifs as the basis of a directed link score and distinguishing such formal/model-specific directed events from generic undirected common-neighbor language.
- **Claim boundary:** The paper's potential theory and bi-fan mechanism are its own formal concepts; they should not be presented as universal facts about all directed networks. Its reported experiments are not evidence for the manuscript's 30 event-first MCAR/MNAR-out masks, the two named datasets, ERGM MPLE conditional-footprint comparisons, or any neural benchmark.

### 3. Yin, Benson, and Ugander (2020)

- **Authors:** Hao Yin, Austin R. Benson, and Johan Ugander
- **Year:** 2020
- **Title:** “Measuring directed triadic closure with closure coefficients”
- **Venue:** *Network Science* 8(4), 551–573
- **DOI:** [10.1017/nws.2020.20](https://doi.org/10.1017/nws.2020.20)
- **Publisher record:** [Cambridge University Press](https://www.cambridge.org/core/journals/network-science/article/measuring-directed-triadic-closure-with-closure-coefficients/AC84C4CF8198E97DE659FED95F64859D)
- **Source type:** Peer-reviewed original research article
- **What it supports:** This source provides an authoritative directed-local-structure vocabulary. It introduces eight directed closure coefficients indexed by labeled wedge types, explicitly distinguishing the **initiator** from the **center** of a directed wedge, and relates their behavior to joint in- and out-degree moments under a directed configuration model. It supports manuscript claims that direction changes the meaning of local closure, that different directed wedge orientations are not interchangeable, and that in/out-degree asymmetry is structurally relevant when defining or interpreting directed local scores.
- **Claim boundary:** The article's machine-learning experiments and AUC values are not needed for, and should not be used to imply, a neural benchmark in the manuscript. This citation supports definitions and structural interpretation of directed closure coefficients, not the manuscript's missingness masks, ERGM estimation, or bounded temporal diagnostic.

## Source-selection note

Together, the three sources cover (i) the general link-prediction/local-index framework and the need for direction-aware modifications, (ii) an original motif-based directed missing-link predictor, and (iii) a rigorous distinction among directed wedge/closure orientations and in/out-degree asymmetry. None is being used to substantiate the manuscript's empirical estimates or to imply forecasting beyond the explicitly bounded temporal diagnostic.
