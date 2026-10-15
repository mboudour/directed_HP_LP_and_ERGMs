# Journal Targeting Research: Directed Network Prediction Under Missingness

## Decision in brief

**Recommended primary target: _Social Network Analysis and Mining_ (SNAM).**
**Fallback target: _Journal of Computational Social Science_ (JCSS).**

This is a ranking of **editorial fit**, not an estimate of review outcome, acceptance rate, or acceptance probability. The manuscript is best understood as a **reproducible, missingness-centred methodological benchmark for directed social networks**: it compares static ERGM MPLE conditional-footprint scores with directed local scores under fixed, leakage-safe MCAR and MNAR-out masks; it treats event-first masking and formal-concept versus native-event fidelity as part of the estimand; and it uses chronology only as a deliberately bounded diagnostic. It is **not** a new machine-learning algorithm, a comprehensive neural benchmark, a full generative ERGM inference paper, or a temporal forecasting paper.

SNAM is the most receptive venue for that exact contribution because its stated remit explicitly joins social-network modeling, data preparation, link/node prediction, and network dynamics with practical, experimental, and theoretical network analysis [1]. That combination gives the paper a natural home without requiring it to impersonate a general graph-learning advance. JCSS is the strongest fallback because it explicitly welcomes reproducible computational social-science methodology, complex systems, and simulation-based statistical inference [7]; it will, however, expect the social-network and observation-failure implications to be especially clear.

## What the paper should claim—and what it should not

> **Proposed one-sentence contribution statement:** In two directed communication/knowledge-exchange networks, a fixed, leakage-safe MCAR/MNAR-out masking protocol shows how defined observation failures alter the comparative behaviour and uncertainty of directed local link-prediction scores and static ERGM MPLE conditional-footprint scores.

Use the following boundaries consistently in the title, abstract, introduction, results headings, and conclusion:

- **Scope:** a static, directed-network prediction benchmark under specified observation/missingness mechanisms.
- **Prediction interpretation:** ERGM MPLE conditional footprints are interpretable conditional statistical-model scores; they are not claimed to be joint MCMC-based ERGM inference or universal generative forecasts.
- **Time interpretation:** the chronological component is a diagnostic check, not a TERGM/STERGM/RHEM analysis or a full temporal forecasting study.
- **Method-comparison interpretation:** the comparison is intentionally between structural, model-based conditional scoring and directed local scoring. It is not a leaderboard of all contemporary graph ML and does not establish superiority over neural link-prediction systems.
- **External-validity interpretation:** conclusions are bounded to Enron and MathOverflow and the 30 fixed masks for each specified mechanism. Report uncertainty/effect sizes across masks, not universal generalization.

Define *hyperlink prediction*, *native directed event*, *formal concept/cap-first representation*, the information boundary at scoring time, and the practical consequences of each representation before presenting metrics. State why masks are event-first, how MCAR and MNAR-out differ, and exactly what observations are unavailable to every score. Make code, mask seeds/indices, data-processing provenance, and a legally accurate data/code-availability statement prominent.

## Ranked editorial-fit assessment

| Rank | Journal | Editorial fit | Why it ranks here | Submission framing change required (without changing analytical scope) |
|---:|---|---|---|---|
| 1 | **Social Network Analysis and Mining** | **High — strongest exact fit** | Its explicit coverage of social-network modeling, data preparation, link/node prediction, and dynamics directly accommodates a directed, missingness-aware network-methods benchmark [1]. Its recent methods-oriented review and empirical NLP/network article support structured methodological comparison when it produces an interpretable insight rather than a narrow score table [2] [3]. | Lead with the missingness-specific methodological result and reproducible protocol. Present ERGM conditional footprints as an interpretable statistical baseline; define the representations for a broad network-science readership; retain the static/diagnostic boundaries visibly. |
| 2 | **Journal of Computational Social Science** | **High — best fallback** | JCSS explicitly accepts technically sound, replicable empirical and methodological work on social/economic structures, complex systems, and simulation-based statistical inference [7] [8]. Recent network link-prediction and centrality work indicate topical receptivity [9] [10]. | Recast the paper as a computational-social-science lesson about observation failure in directed communication/knowledge networks. Explain the social-science stakes of missing outgoing events, articulate replication materials, and do not frame results as general forecasting superiority. |
| 3 | **Data Mining and Knowledge Discovery** | **High topic fit; conditional editorial fit** | Prediction, probabilistic modelling, uncertainty/noise, preprocessing, dependency analysis, and evaluation are in scope [4]. Its official graph-focused editorial signals welcome benchmarks, robustness/reliability, interpretable methods, and empirical evaluation [5] [6]. | Make the reusable benchmark protocol—not the Enron/MathOverflow comparison—the headline. Explicitly justify the deliberately bounded baseline suite and lack of a neural comparator; foreground leakage-safe mask construction, estimands, and interpretable conditional diagnostics. |
| 4 | **Statistical Analysis and Data Mining: The ASA Data Science Journal** | **Moderate** | The statistical-data-mining remit can support missingness-aware directed prediction and ERGM-based conditional scores [16]. Its recent network-statistical and nonignorable-missingness articles are encouraging precedents [17] [18]. | Articulate a transferable statistical lesson about the consequence of MCAR/MNAR-out assumptions, emphasize uncertainty over fixed masks and data/code availability, and avoid presenting the article as software or a simple two-method leaderboard. |
| 5 | **ACM Transactions on Knowledge Discovery from Data** | **Moderate** | Social networks, graph data, preprocessing, robust/scalable statistical methods, and theory–practice connections fit at the topical level [13]. But recent graph papers emphasize a new scalable method or broader technical advance [14] [15]. | Position the fixed-mask design as a general missingness-aware evaluation framework with documented implementation consequences and failure modes. Clearly delimit the static ERGM/local-score question rather than implying a comprehensive graph-discovery benchmark. |
| 6 | **Machine Learning** | **Moderate outer-scope fit; least suitable** | Prediction, probabilistic/statistical models, and research methodology are in scope, but the journal calls for a clear learning component, explicit task/assumptions, and verifiable evidence [11] [12]. Recent graph work highlights contemporary graph/temporal methods or broad controlled forecasting comparisons [19] [20]. | A substantially ML-facing rewrite would be necessary: formalize the supervised task, information set, and transferable evaluation lesson. Because the contribution remains a bounded network-statistical comparison rather than a new learning method, this remains the least natural option. |

### Why the ordering is defensible

1. **SNAM fits the paper’s native discipline and objects of study.** The paper concerns directed social/communication-network prediction, representation fidelity, statistical network modeling, masking, and empirical evaluation—areas named in SNAM’s scope [1]. It can contribute methodological insight without being judged primarily against the novelty standard for a new general-purpose graph-learning algorithm.
2. **JCSS has similarly strong topical fit but a slightly less direct methods home.** It is highly suitable if the manuscript makes the computational-social-science significance of observation failure central. Its recent link-prediction publication also couples network methods to an applied social/economic question [9], making that contextual framing valuable.
3. **DMKD is viable but will judge the work through a broader data-mining novelty lens.** Its graph-focused call supports benchmarks and robustness work [5], yet an established-method comparison on two networks must be presented as a reusable evaluation/diagnostic result rather than as a conventional link-prediction paper.
4. **SAM is a credible statistical alternative, but general statistical novelty is the issue.** The recent precedents show openness to network inference and nonignorable missingness [17] [18], while the present manuscript must make a methodological inference about missingness—not merely describe a benchmark outcome.
5. **TKDD is topical but less aligned with the paper’s deliberately non-algorithmic contribution.** The supplied recent graph examples foreground novel GNN/imputation methods, scalability, and broader data coverage [14] [15]. This paper should not stretch its claim to meet that profile.
6. **Machine Learning is in scope only at a broad outer boundary.** A prediction task and a statistical model do not by themselves make this a natural ML-journal paper; the current contribution is more appropriately network-methodological than algorithmically ML-novel.

## Primary target: Social Network Analysis and Mining

### Why SNAM is most receptive to this exact paper

SNAM’s scope spans practical, experimental, and theoretical data-driven network analysis/mining and expressly includes **social-network modelling and analysis**, **data preparation**, **link/node prediction**, and **network dynamics/evolution** [1]. This manuscript sits at the intersection of those named areas: it tests how the data-preparation/observation mechanism changes directed prediction conclusions and contrasts a statistical-network conditional score with directed local scores.

The proposed contribution also matches the kind of methods-facing insight visible in SNAM’s recent content. Hamed, Rebhi, and Saoud’s review builds a taxonomy and comparison framework for multilayer community detection rather than simply listing methods [2]. Darwish, Abdelmoty, and Turner combine network analysis with hybrid NLP and validation to produce an empirically grounded social-network result [3]. SNAM’s current collections also foreground method-rich themes including community detection, social influence/information dissemination, deep learning in social-network analysis, and the ASONAM journal track [21]. These are **editorial-fit signals**, not evidence that any submission will be accepted.

### Concrete SNAM-facing changes

1. **Retitle/reabstract around the causal question posed by the mask, not a contest between methods.** For example: *Directed link prediction under observation failure: a reproducible MCAR/MNAR-out benchmark of local and ERGM conditional scores.* Avoid “state of the art,” “forecasting,” or “universal.”
2. **State the contribution in three bounded parts:** (i) event-first, leakage-safe masks define the observation scenario; (ii) formal-concept/cap-first and native-event choices are distinct data-generating representations with consequences; and (iii) ERGM conditional footprints provide an interpretable model-based comparator to local scores.
3. **Make reproducibility a result-bearing design feature.** Put the fixed masks, random seeds, preprocessing rules, code, versions, and accessible data/derivation instructions in the manuscript and repository/data-availability statement where legal constraints permit.
4. **Explain technical vocabulary at first use.** Give an intuitive directed-event example for hyperlink prediction and a short explanation of why a formal concept is not always a native observed event. Translate MPLE conditional footprints into what information the score uses and does not use.
5. **Use uncertainty and limitation language throughout.** Show variation across the 30 masks; say what the two networks and bounded diagnostic do not establish. Do not add a promise of neural, joint-MCMC, TERGM/STERGM/RHEM, or full forecasting coverage.

## Fallback target: Journal of Computational Social Science

### Why JCSS is the appropriate fallback

JCSS explicitly spans computational analyses of social and economic phenomena and structures across social science, physics, biology, management science, computer science, and data science; its scope includes complex systems and simulation-based statistical inference, with replicable empirical, theoretical/methodological, data, and software contributions [7] [8]. The paper’s directed Enron and MathOverflow networks, observation-failure mechanism, and reproducible comparison of conditional statistical and local scores can therefore be framed as a methodological contribution to **computational social-network analysis**.

Recent JCSS examples provide a well-matched, though not identical, precedent: Lu et al. use network analysis and ML link prediction in a social/economic network context [9], and Bendahman and Lotfi introduce and validate a network centrality method across heterogeneous social networks [10]. The implication is to make both the methodological and social-network relevance explicit—not to add a new algorithm or expand the analytical scope.

### Concrete JCSS-facing changes

1. **Open with the substantive methodological problem:** communication and knowledge-exchange networks are observed imperfectly, and missing outgoing events can alter structural conclusions. Tie the protocol to how an analyst should interpret directed-network evidence.
2. **Describe the benchmark as a replicable computational-methods contribution.** Make the mask-generation recipe, estimands, information boundary, evaluation metrics, and availability statement easy to audit.
3. **Center interpretability.** Explain what ERGM conditional footprints diagnose about structural effects under observation loss relative to local heuristics, rather than presenting ERGM as a black-box competitor.
4. **Use the chronological result only as a diagnostic robustness boundary.** Say explicitly that it does not support a claim about dynamic social-network forecasting.
5. **Bound social inference.** Enron and MathOverflow illustrate two directed network settings; they do not identify a universal behavioural mechanism or establish broad external validity.

## Why the other venues are less suitable

### Data Mining and Knowledge Discovery

DMKD’s scope is genuinely supportive: it names uncertainty management, data cleaning/noise modelling, probabilistic modelling, prediction/estimation, dependency analysis, preprocessing, evaluation, and explanation [4]. The official graph-focused material also values methods, metrics/benchmarks, robustness/reliability, interpretable work, and dynamic/evolving graphs [5] [6]. Its risk is not topical mismatch but **editorial expectation**: the manuscript could be mistaken for a narrow ERGM-versus-local-score experiment unless the fixed masking protocol and its transferable diagnostic lesson are unmistakably primary. Submit only after the broad data-mining/evaluation framing is fully credible.

### Statistical Analysis and Data Mining

SAM is hospitable to statistically grounded data mining and expects intellectual importance, novelty, general properties or applicability, convincing comparative evidence, and data/code sharing [16]. Network centrality inference and nonignorable-missingness Bayesian inference are relevant recent examples [17] [18]. The paper has a plausible home here, but it has less theoretical/statistical-method development than those signals may lead readers to expect. Its comparative design must yield a sharply stated general finding about observation mechanisms and conditional prediction; otherwise it risks looking limited to two application datasets.

### ACM Transactions on Knowledge Discovery from Data

TKDD’s topical scope includes graph-structured data and social-network analysis [13], and its recent papers demonstrate interest in graph link prediction and mask-aware graph imputation [14] [15]. Yet the supplied graph precedents emphasize new methods, scalability/theory, multiple datasets, or broad empirical scope. This manuscript’s intentional contribution is a **bounded, interpretable static benchmark**, not a new GNN, imputation model, or scalable discovery algorithm. It should not be forced into TKDD’s stronger algorithmic-novelty signal.

### Machine Learning

The journal’s official criteria require a clear learning component, stated task/assumptions, replicable evidence, and positioning in ML literature [11] [12]. Its recent graph/temporal prediction and missingness/forecasting studies demonstrate relevance to graph prediction and controlled missingness experiments [19] [20], but also signal expectations of identifiable ML novelty, contemporary model comparison, realistic protocols, or substantial forecasting coverage. Since the paper intentionally lacks a successful neural benchmark and does not claim full temporal prediction, this is the least aligned of the six. A network-science/statistical-network journal is the better match.

## Submission checklist common to both top targets

- [ ] The title and abstract call this a **static, missingness-centred, directed-network benchmark**, not a universal link-prediction or forecasting study.
- [ ] The research question, estimand, held-out objects, and score-time information boundary are defined before results.
- [ ] MCAR and MNAR-out mask construction is reproducible and demonstrably leakage-safe; all 30 fixed masks and seeds/identifiers are available where permitted.
- [ ] Event-first masking and the formal-concept/cap-first versus native-event distinction are explained as representation/observation choices with practical consequences.
- [ ] The ERGM method is accurately labeled as MPLE conditional-footprint scoring; it is not conflated with joint MCMC ERGM inference.
- [ ] Results report uncertainty/effect sizes across masks and computational failures/costs where relevant; conclusions do not extend beyond the two datasets and specified mechanisms.
- [ ] The limitation paragraph explicitly excludes successful neural benchmarking, MCMC-derived joint L3 results, TERGM/STERGM/RHEM modelling, and full forecasting from the claim set.
- [ ] Repository, code, environment, mask, data-access, and licensing/legal limitations are stated transparently.

## References

[1]: https://link.springer.com/journal/13278/aims-and-scope "Social Network Analysis and Mining: Aims and scope"
[2]: https://link.springer.com/article/10.1007/s13278-024-01266-1 "A comprehensive view of community detection approaches in multilayer social networks"
[3]: https://link.springer.com/article/10.1007/s13278-025-01516-w "Analysing social network structures and thematic engagement on X audio spaces"
[4]: https://link.springer.com/journal/10618/aims-and-scope "Data Mining and Knowledge Discovery: Aims and scope"
[5]: https://link.springer.com/journal/10618/updates/27773304 "Knowledge Discovery from Graphs"
[6]: https://link.springer.com/article/10.1007/s10618-024-01041-y "Explainable and Interpretable Machine Learning and Data Mining"
[7]: https://link.springer.com/journal/42001/aims-and-scope "Journal of Computational Social Science: Aims and scope"
[8]: https://link.springer.com/journal/42001/submission-guidelines "Journal of Computational Social Science: Submission guidelines"
[9]: https://link.springer.com/article/10.1007/s42001-024-00341-z "Network analysis and machine-learning link prediction for bilateral investment treaties"
[10]: https://link.springer.com/article/10.1007/s42001-026-00471-6 "Influence-disparity centrality methodology"
[11]: https://link.springer.com/journal/10994/aims-and-scope "Machine Learning: Aims and scope"
[12]: https://link.springer.com/journal/10994/submission-guidelines "Machine Learning: Submission guidelines"
[13]: https://dl.acm.org/journal/tkdd/about "ACM Transactions on Knowledge Discovery from Data: About the journal"
[14]: https://dl.acm.org/doi/10.1145/3640347 "Asymmetric Learning for Graph Neural Network Based Link Prediction"
[15]: https://dl.acm.org/doi/10.1145/3743141 "MagiNet: Mask-Aware Graph Imputation Network for Traffic Data"
[16]: https://onlinelibrary.wiley.com/page/journal/19321872/homepage/productinformation.html "Statistical Analysis and Data Mining: Journal information and scope"
[17]: https://onlinelibrary.wiley.com/doi/abs/10.1002/sam.11712 "Node Centrality Inference via Hypothesis Testing"
[18]: https://onlinelibrary.wiley.com/doi/abs/10.1002/sam.11667 "Bayesian inference for nonprobability samples with nonignorable missingness"
[19]: https://link.springer.com/article/10.1007/s10994-024-06579-y "Temporal graph transaction prediction / T3GNN"
[20]: https://link.springer.com/article/10.1007/s10994-024-06651-7 "Controlled data-sparsity/missingness comparison of statistical, XGBoost, and deep-learning forecasting models"
[21]: https://link.springer.com/journal/13278/collections "Social Network Analysis and Mining: Journal collections"
