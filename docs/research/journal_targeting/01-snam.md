# Social Network Analysis and Mining — tentative target assessment

**Editorial fit: High (fit only; not a prediction of acceptance).** The paper is squarely within SNAM’s stated remit: the journal solicits practical, experimental, and theoretical work on data-driven network analysis and mining using statistics, mathematics, physics, network science, data science, and computer science methods. Its listed topics explicitly include social-network modeling and analysis, data collection and preparation, link and node prediction, and the dynamics/evolution of social networks. [1]

## Why the paper fits

The proposed manuscript’s core is a reproducible network-methods benchmark: directed local link-prediction scores are compared with static ERGM MPLE conditional-footprint scores under controlled MCAR and MNAR-out missingness, using Enron and MathOverflow. That maps directly to SNAM’s network-analysis/modeling, data-preparation, and link-prediction scope. The fact that the contribution is comparative and methodological rather than a new general machine-learning algorithm is not, by itself, a mismatch: SNAM’s scope explicitly welcomes theoretical and experimental work, not only deep learning or AI advances. [1]

The journal’s recent content also shows room for methodological comparisons and structured syntheses. A 2024 review paper presents a taxonomy and a “four worlds framework” for comparing community-detection methods in static and dynamic multilayer networks, while identifying unresolved challenges. [2] A 2025 original article combines bipartite-to-projected network analysis with a hybrid BERT/spaCy/expert-validation method and emphasizes novel empirical insights from a new social-platform dataset. [3] Together, these examples suggest that a benchmark can fit when it makes a clear methodological contribution and explains what the results reveal about social-network analysis, rather than reading as a narrow leaderboard.

SNAM’s official collections page currently lists an ASONAM journal track, Advanced Methods in Community Detection, Social Influence and Information Dissemination in Networks, and Deep Learning in Social Network Analysis, among others. This reinforces an editorial interest in network methods, comparative analysis, and prediction, although the collection titles are not evidence that this specific paper would be accepted. [4]

## Main suitability risk and framing expectations

The manuscript should make the missingness-centered benchmark itself the methodological contribution. It should clearly distinguish dyadic arcs, cap-first formal concepts, and native directed events; define why MCAR and MNAR-out masks represent substantively different observation failures; and report uncertainty and reproducibility details for all 30 fixed masks. Without that framing, reviewers could see the work as a limited comparison of familiar local scores against a static ERGM MPLE implementation.

The strongest editorial risk is breadth of validation. The manuscript has no successful neural benchmark, no MCMC-derived joint L3 result, and no full forecasting/TERGM/STERGM/RHEM analysis. Those omissions do not contradict the published scope, but they may matter if the paper claims broad superiority, general “link prediction” conclusions, or temporal forecasting relevance. The title, abstract, and conclusion should instead state a bounded claim: a controlled benchmark of static ERGM conditional-footprint scores versus local directed link-prediction scores under specified missingness mechanisms, on two fixed datasets, with only a limited chronological diagnostic.

A second risk is audience accessibility. “Hyperlink prediction,” cap-first formal concepts, and native directed events may be unfamiliar or interpreted inconsistently by a broad social-network readership. The paper should connect each distinction to a concrete modeling or evaluation consequence and explain what practitioners gain from the benchmark. The Enron and MathOverflow cases should be justified as complementary network types, while the two-dataset limit should be acknowledged as a boundary on external validity.

SNAM’s ASONAM 2024 journal-track call is informative about standards even though that call is closed: it required high-quality journal-level work, excluded survey papers and journal versions of previously published conference papers for that track, and encouraged (indeed, for that track, required repository-style availability of data and software for reproducibility). [5] For a regular submission, the safest positioning is therefore an original, reproducible methods paper with a precise contribution and openly documented code/data access where legally possible—not a claim that the study is a complete state-of-the-art forecasting survey.

## Recommendation

**Submit only after sharpening the methodological framing and claims.** SNAM is a credible high-fit target for the static ERGM/missingness/network-methods emphasis. It is not necessary to add a neural model merely to satisfy scope, but the manuscript should pre-empt the obvious question by explaining why the benchmark’s purpose is to establish a transparent statistical baseline and diagnose missingness sensitivity, not to declare a universal winner. It should also label the chronological analysis as diagnostic rather than full dynamic modeling. Editorial fit is high; this assessment deliberately makes no claim about acceptance probability or acceptance rate.

## References

[1]: https://link.springer.com/journal/13278/aims-and-scope "Social Network Analysis and Mining — Aims and scope"

[2]: https://link.springer.com/article/10.1007/s13278-024-01266-1 "A comprehensive view of community detection approaches in multilayer social networks (2024)"

[3]: https://link.springer.com/article/10.1007/s13278-025-01516-w "Analysing social network structures and thematic engagement on X audio spaces (2025)"

[4]: https://link.springer.com/journal/13278/collections "Social Network Analysis and Mining — Collections and calls for papers"

[5]: https://link.springer.com/journal/13278/updates/26858222 "Social Network Analysis and Mining — ASONAM 2024 Journal Track call"
