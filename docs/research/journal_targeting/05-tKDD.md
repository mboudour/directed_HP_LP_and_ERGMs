# ACM Transactions on Knowledge Discovery from Data (TKDD)

**Editorial fit: Moderate (fit is not a probability-of-acceptance estimate).**

## Current official scope

TKDD says it welcomes research on “knowledge discovery and analysis of diverse forms of data.” Its listed topics include effective/scalable data-mining algorithms; mining spatial and temporal data; community generation; **social-network analysis and graph-structured data**; preprocessing and post-processing; robust and scalable statistical methods; and foundations of data mining. It also welcomes theoretical work that addresses applicability or implementability, and applications that expose issues current data-mining technology cannot satisfy. [1]

The candidate paper is therefore in-scope at the subject level: directed social/network data, link/hyperlink prediction, missingness-aware preprocessing/evaluation, and ERGM-based statistical modeling all map directly to TKDD’s stated social-network, graph, preprocessing, robust-statistics, and data-mining-foundations interests. The paper’s reproducibility emphasis and fixed MCAR/MNAR-out masks are potentially useful as a methodological benchmark for knowledge-discovery evaluation rather than as a sociology-only result.

## Editorial expectations and fit

TKDD’s guidelines state that it publishes original archival papers in data science, knowledge discovery, data mining, and closely related disciplines; submissions are judged primarily on **originality and relevance**, with effective presentation also critical. The journal encourages submissions that significantly contribute to new or important research areas, and emphasizes significant improvement over the state of the art rather than manuscript length. [2]

The strongest fit is a clearly framed **missingness-centred evaluation methodology for directed graph discovery**: distinguish dyadic arcs, cap-first formal concepts, and native directed events; make event-first MCAR/MNAR-out masking explicit; and show how missingness changes conclusions about local link-prediction scores versus static ERGM MPLE conditional-footprint scores. That framing speaks to data-quality-aware graph mining and robust statistical evaluation, not merely to an empirical comparison of two model families.

The paper should also make the theory–practice bridge explicit. TKDD specifically encourages theory papers to discuss applications and implementation consequences, and systems/applications papers to connect to relevant theory. [2] For this manuscript, that means explaining when ERGM MPLE scores are computationally practical, what the conditional footprint does and does not measure, how masks affect deployable discovery pipelines, and why Enron and MathOverflow are informative beyond being convenient datasets.

Recent official TKDD content shows that graph link prediction is a legitimate venue topic, but also illustrates the novelty bar. Yao and Li’s 2024 TKDD article proposes a new asymmetric-learning method for GNN link prediction, analyzes a scalability bottleneck, and evaluates on three large-scale datasets with training-speed comparisons. [3] This supports topical fit for directed link prediction and graph methods, but it also signals that a manuscript using only established local scores and static ERGM MPLE needs a sharper methodological contribution than “ERGM performs competitively.” Its contribution should be a defensible evaluation protocol, a new missingness taxonomy/diagnostic, or substantive generalizable findings about when model rankings are invalidated by missingness.

A second recent TKDD example, Zhou et al.’s 2025 **MagiNet**, treats missingness directly in graph-structured data, reports MCAR experiments on five real-world traffic datasets, and releases code. [4] This is favorable evidence that missing-data mechanisms and graph structure are editorially relevant. It also makes the candidate’s reproducibility package, precise mask-generation protocol, released code/data manifests, and uncertainty/limitations discussion important for credibility.

## Likely barriers or framing risks

- **Novelty may look incremental if framed as a two-model benchmark.** Static ERGM MPLE and local LP scores are established ingredients. The manuscript must establish what new scientific knowledge the mask design, directed-event distinctions, and conditional-footprint comparison produce, and why those insights transfer beyond two datasets.
- **The scope is intentionally limited.** The absence of a successful neural benchmark, MCMC-derived joint-L3 result, and full forecasting/TERGM/STERGM/RHEM analysis is not automatically disqualifying, but reviewers may view the benchmark as incomplete unless the paper explicitly defines its question as static, reproducible, missingness-centred evaluation. Do not imply comprehensive forecasting or modern graph-learning coverage.
- **A weak baseline suite could hurt relevance.** The paper should include a transparent rationale for the selected local LP baselines and ERGM MPLE scores, report computational costs and failure modes, and state what conclusions cannot be drawn without neural, temporal, or MCMC joint models. If feasible, add at least a clearly identified non-neural statistical baseline or a robust negative-control analysis; otherwise make the omission a deliberate boundary condition.
- **Dataset breadth and external validity are concerns.** Enron and MathOverflow provide useful directed social/event data, but two networks may not support broad claims. The paper should avoid claiming universal superiority and instead report effect sizes, uncertainty across the 30 fixed masks, sensitivity to MCAR versus MNAR-out, and a limited chronological diagnostic as exactly that—a diagnostic.
- **Terminology and task alignment must be unusually clear.** TKDD’s broad audience will need concise definitions separating dyadic arcs, cap-first formal concepts, native directed events, missing links, and withheld future events. The paper should connect each object to a data-mining task and evaluation target, not assume a network-science specialist reader.
- **Originality/disclosure requirements still apply.** If any part is based on a prior paper, TKDD requires a major value-added extension and at least 30% new content, with overlapping prior work disclosed. [2]

## Recommendation

**Tentative target: submit only after reframing and strengthening the contribution narrative; otherwise choose a more network-science/statistical-methods venue.** TKDD is a defensible target because the topic sits squarely within its official social-network/graph, preprocessing, and robust-statistical scope. I would call the current editorial fit **moderate rather than high** because the described study is deliberately a benchmark and diagnostic, while recent TKDD examples foreground a novel algorithm, theory, or large-scale empirical advance. A TKDD submission should lead with a generalizable missingness-aware evaluation framework and reproducible protocol, quantify what changes inferences about directed link prediction, and be explicit that it is not a comprehensive neural or temporal-network benchmark. This assessment concerns editorial fit only; it does not estimate acceptance probability.

## Citations

[1]: https://dl.acm.org/journal/tkdd/about "ACM TKDD About: official aims, scope, and subject coverage"

[2]: https://dl.acm.org/journal/tkdd/author-guidelines "ACM TKDD Author Guidelines: originality, relevance, contribution, and prior-publication requirements"

[3]: https://dl.acm.org/doi/10.1145/3640347 "Asymmetric Learning for Graph Neural Network based Link Prediction, ACM TKDD, 2024"

[4]: https://dl.acm.org/doi/10.1145/3743141 "MagiNet: Mask-Aware Graph Imputation Network for Traffic Data, ACM TKDD, 2025"
