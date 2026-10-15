# Statistical Analysis and Data Mining — tentative target assessment

**Paper assessed:** “Exponential Random Graph Models as a Benchmark for Directed Link and Hyperlink Prediction under Missingness.”

## Current official scope

The journal is *Statistical Analysis and Data Mining: The ASA Data Science Journal*, published on behalf of the American Statistical Association. Its official aims say it is primarily a statistical journal focused on **novelty, intellectual importance, and relevance** in contemporary statistics, statistical machine learning, and statistical data mining. It welcomes innovative analytic techniques and applications when grounded in mathematical rigor, and expects methods to be developed far enough that key general properties can be established and applicability assessed. It also welcomes review articles on broadly important current statistical topics. [1]

The reviewer guidance is especially material for this manuscript: the paper should state a clear, important contribution; methodology, computational approach, or theory should be logically streamlined; and a new method should explain when it is better than existing methods, supported by theory, systematic simulations, or another convincing argument. An application demonstrating feasibility is usually desirable. [1] The author guidance also says the journal expects associated datasets, code, and software to be uploaded or made available through a repository, with a data-availability statement. [2]

## Editorial fit

**Editorial fit: Moderate.** This is a credible, but not automatic, target. The paper’s statistical-network methods are within the journal’s broad scope: it is a methodological/computational study of prediction under missingness, compares local link-prediction scores with ERGM MPLE conditional-footprint scores, distinguishes directed arcs from cap-first formal concepts and native directed events, and uses reproducible MCAR/MNAR masking experiments on real networks. The missingness emphasis, simulation-style benchmarking, and public/reproducible computational framing align well with the journal’s stated interest in statistical data mining, modeling and simulation, computationally intensive methods, and practical data analysis. [1] [2]

The static ERGM component is not out of scope. A recent article in the journal proposes a hypothesis-testing centrality method using a random-graph model, derives an analytical p-value and bound, and evaluates it on simulated and real networks; this shows that network-statistical methodology can be presented as a substantive statistical contribution rather than only as a social-network application. [3] A separate 2024 article develops a Bayesian approach for nonprobability samples with nonignorable missingness, uses simulation studies, and compares performance on real datasets. That precedent is informative for the paper’s MCAR/MNAR framing and its emphasis on empirical assessment of a missingness-aware statistical procedure. [4]

The strongest fit argument is therefore not “ERGM is a network model,” but that the manuscript offers a carefully controlled, reproducible statistical benchmark that tests how missingness mechanisms alter directed prediction and how a model-based conditional footprint compares with conventional local scores. To make that argument persuasive to this journal, the paper should foreground generalizable statistical lessons about missingness and benchmark design, not only the Enron and MathOverflow findings.

## Novelty and framing risks

The main risk is the journal’s explicit novelty bar. Because the contribution is comparative and methodological rather than a new general-purpose learning algorithm, editors may view it as an evaluation paper unless the manuscript makes a clear, non-incremental claim about **what is learned statistically** from the benchmark. The introduction should state a compact contribution that goes beyond “we compare methods,” such as a principled result about when ERGM conditional footprints remain competitive or fail under specific directed MCAR/MNAR observation mechanisms, and why that result transfers beyond the two datasets.

The paper should avoid implying broader forecasting or dynamic-network coverage that it does not provide. It has only a limited chronological diagnostic and does not contain a full TERGM/STERGM/RHEM analysis, a successful neural baseline, or an MCMC-derived joint L3 result. Those omissions are not inherently disqualifying for scope, but reviewers may ask whether the benchmark is sufficiently complete for claims about directed link/hyperlink prediction. The framing should explicitly delimit the paper as a **static, missingness-centred benchmark** and explain why the chosen baselines answer that narrower question.

A second risk is methodological completeness. The official guidance asks authors to support claims with theory, systematic simulations, or other evidence and to establish key general properties where applicable. [1] Thirty fixed MCAR and MNAR event-first masks across two real networks are a useful reproducible design, but reviewers may expect sensitivity analyses over missingness severity, mechanism parameters, graph statistics, or synthetic graph families. If those are infeasible, the manuscript should label the work as a benchmark/diagnostic study and state the limits of external validity rather than presenting the datasets as representative.

A third risk is that ERGM MPLE may be judged too narrow or computationally convenient if the manuscript does not explain the estimand and comparison protocol carefully. The paper should distinguish predictive scoring from generative fit, clarify leakage control and train/test construction under every mask, report uncertainty across masks, and explain why MPLE conditional footprints are the appropriate ERGM comparator when no joint MCMC L3 result is claimed. Reproducibility is a strength, but it does not substitute for a clearly motivated statistical estimand.

## Recommendation

**Tentative recommendation: submit only after sharpening the statistical novelty and scope.** The journal is a plausible moderate-fit destination for a rigorous version centered on missingness-aware statistical benchmarking in directed networks. It is less suitable if the paper reads primarily as a software/benchmark report, a social-network case study, or an incomplete survey of all possible link-prediction models. The cover letter should emphasize: (1) the general missingness-design contribution, (2) the precise statistical interpretation of ERGM conditional footprints versus local scores, (3) systematic uncertainty/reporting across the 30 masks, and (4) complete code/data availability. This is an editorial-fit judgment only, not a probability-of-acceptance estimate.

## References / citations

[1]: https://onlinelibrary.wiley.com/page/journal/19321872/homepage/productinformation.html "Statistical Analysis and Data Mining — Overview, Aims and Scope, and Guidelines for Reviewers"

[2]: https://onlinelibrary.wiley.com/page/journal/19321872/homepage/forauthors.html "Statistical Analysis and Data Mining — Author Guidelines, Aims and Scope, and Data/Code Requirements"

[3]: https://onlinelibrary.wiley.com/doi/abs/10.1002/sam.11712 "Node Centrality Inference via Hypothesis Testing"

[4]: https://onlinelibrary.wiley.com/doi/abs/10.1002/sam.11667 "Bayesian inference for nonprobability samples with nonignorable missingness"
