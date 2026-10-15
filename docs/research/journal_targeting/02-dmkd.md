# Data Mining and Knowledge Discovery — tentative target assessment

**Editorial fit: High (but not excellent).** This is a fit judgment, not a prediction of acceptance probability; no acceptance-rate claim is made.

## Current official scope

Springer’s current aims and scope describes *Data Mining and Knowledge Discovery* (DMKD) as a technical venue for extracting useful patterns and models from raw data stores, including data cleaning and noise modelling, scalability, and making discovered patterns understandable. It explicitly welcomes original technical research and practice papers, surveys/tutorials, and detailed applications. Its listed scope includes structured-data representation, uncertainty management, metrics of interestingness/utility, probabilistic modelling, prediction and estimation, dependency analysis, preprocessing (including cleaning, selection, sampling and reduction), evaluation/consolidation/explanation of discovered knowledge, and application case studies. [1]

That scope maps well to the proposed paper’s core: a reproducible benchmark of directed link/hyperlink prediction under MCAR and MNAR-out missingness; explicit distinctions among dyadic arcs, cap-first formal concepts, and native directed events; comparative local link-prediction scores versus static ERGM MPLE conditional-footprint scores; and an evaluation protocol with fixed masks and a limited chronological diagnostic. The manuscript is therefore more naturally framed as a **data-mining methods/evaluation paper about structured relational data, missingness, uncertainty, and model comparison** than as a contribution to social-network theory alone.

## Evidence from recent official DMKD material

* The official 2025 “Knowledge Discovery from Graphs” special-issue description is especially favorable evidence. It solicits graph data and graph-based technologies, novel theoretical frameworks for knowledge extraction from graphs, dynamic/heterogeneous graph processing, and—explicitly—“new metrics and benchmarks,” empirical evaluations, and robustness/reliability analysis. It also names social-media analysis, interpretable methods, and dynamic/evolving graphs. [2] A missingness-centred directed link/hyperlink benchmark fits these themes, although the call’s examples lean toward newer graph-learning and scalable graph methods.
* The 2024 official guest editorial for the “Explainable and Interpretable Machine Learning and Data Mining” collection presents DMKD as a venue for methodological work on appropriate learning formalisms, interpretation/explanation techniques, metrics, and assessment options, including interpretable (white-box) models. [3] Static ERGM conditional footprints can be positioned as an interpretable probabilistic baseline and as a way to audit what missingness does to structural signals, but the paper should make that explanatory/evaluation value explicit rather than present ERGM only as a legacy comparator.

## Fit and likely editorial pressure points

The **static ERGM/missingness/network-methods emphasis is within scope** because DMKD explicitly includes probabilistic modelling, prediction/estimation, dependency analysis, preprocessing/noise modelling, and evaluation. The paper’s reproducibility and fixed-mask design are positive signals for a methods-and-benchmark readership. Its limited chronological diagnostic is also defensible if presented as a deliberately bounded diagnostic rather than as a forecasting claim.

The main risk is not topical mismatch; it is **novelty and framing**. DMKD’s graph call emphasizes advances in graph mining/learning, scalable or dynamic graph processing, novel frameworks, new benchmarks/metrics, and empirical state-of-the-art comparison. A paper that reads as “ERGM versus familiar local scores on two networks” could be judged incremental, narrow in data breadth, or insufficiently connected to general data-mining knowledge discovery. The manuscript should foreground what is novel and reusable in the benchmark protocol: event-first semantics, cap-first hyperedge handling, explicit MCAR/MNAR-out estimands, leakage-safe masking, and the conditional-footprint interpretation of MPLE. It should explain why these design choices expose failure modes that ordinary link-prediction benchmarks miss.

The absence of a successful neural benchmark is not automatically disqualifying, but it weakens a state-of-the-art claim under the graph-mining framing. The manuscript should avoid implying that it comprehensively benchmarks modern graph ML. It should state the comparison boundary clearly and, if feasible, include a carefully selected non-neural and/or simple learned baseline—or justify why the paper’s question is about missingness and structural interpretation rather than leaderboard performance. Likewise, no MCMC-derived joint L3 result and no full forecasting/TERGM/STERGM/RHEM analysis are acceptable only if the paper does not claim full generative ERGM inference, dynamic-network forecasting, or comprehensive temporal-event modeling. Reviewers may still request stronger temporal and generative baselines if the title or conclusions overreach.

Two-network coverage (Enron and MathOverflow) also calls for restrained generalization. The contribution should be sold as a **reproducible benchmark and diagnostic framework**, not as a universal ranking of link-prediction methods. Clear limitations around network diversity, MNAR mechanism assumptions, MPLE versus MCMC, and the bounded chronological check will help editorial fit.

## Recommendation

**Tentative target: submit only after reframing toward DMKD’s data-mining contribution.** On topic, the fit is high; the paper is not an obvious mismatch. To improve suitability, make the benchmark protocol and missingness methodology the primary contribution, connect ERGM scores to interpretable probabilistic/dependency modelling, report robust comparative uncertainty/significance analyses, and explicitly delimit claims about neural methods, temporal forecasting, and full ERGM inference. If the manuscript remains primarily a social-network-methods paper with limited methodological generalization, a network-science venue may be a better editorial home.

## Citations

[1]: https://link.springer.com/journal/10618/aims-and-scope "Data Mining and Knowledge Discovery — Aims and scope"
[2]: https://link.springer.com/journal/10618/updates/27773304 "Data Mining and Knowledge Discovery — Special Issue on Knowledge Discovery from Graphs"
[3]: https://link.springer.com/article/10.1007/s10618-024-01041-y "Explainable and interpretable machine learning and data mining"
