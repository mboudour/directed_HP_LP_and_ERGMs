# Journal targeting note: Journal of Computational Social Science

**Paper assessed:** “Exponential Random Graph Models as a Benchmark for Directed Link and Hyperlink Prediction under Missingness.”

## Editorial-fit judgment

**Editorial fit: high (with a material framing risk).** This is a plausible target for JCSS because the journal explicitly seeks interdisciplinary computational research on social/economic phenomena or structures, including complex systems, simulation-based statistical inference, numerical optimization, high-performance computing, and related computational methods. Its scope is not limited to machine learning. [1]

The paper’s reproducible benchmark is therefore substantively aligned: it studies social-network structures with computational methods; compares directed local link-prediction scores with ERGM MPLE conditional-footprint scores; treats missingness as a central methodological problem; and uses real social-network data (Enron and MathOverflow) plus controlled MCAR and MNAR-out masks. The static ERGM emphasis is not, by itself, disqualifying: JCSS’s stated scope includes complex systems and simulation-based statistical inference, while its submission criteria expressly recognize a “new theoretical or methodological result” usable to analyze social/economic phenomena or structures computationally. [1] [2]

Recent journal content supports this reading. A 2024/2025 JCSS research article used network analysis and machine-learning link prediction on bilateral-investment-treaty data, combining network features such as Jaccard, resource allocation, and Adamic–Adar with tree-based prediction models. That paper shows that link prediction and network-method applications are within the journal’s editorial territory, although its framing is an empirical policy question and its novelty is a combined application/modeling approach. [3] A 2026 JCSS article introduced a new centrality measure, validated it across heterogeneous social-network datasets, and evaluated it with diffusion simulations. This indicates receptivity to network-method innovation when the methodological contribution is explicit and validated beyond a single dataset. [4]

## What helps the submission

The strongest fit points are: (1) a computationally explicit methodological contribution rather than a purely descriptive network study; (2) a social-science-facing evaluation on two recognizable communication/Q&A networks; (3) reproducibility and a fixed-mask design that makes performance comparisons auditable; (4) attention to MCAR and MNAR missingness, which gives the paper a clear methodological problem rather than an ordinary leaderboard exercise; and (5) directed arcs, hyperlink/event distinctions, and ERGM-based structural baselines, which can be presented as interpretable social-network methodology rather than as an ML competition.

JCSS also requires that articles be technically sound, sufficiently detailed for replication, and accessible to interdisciplinary audiences. The paper’s reproducible design is a positive match, but the manuscript should make the data/code access, mask-generation procedure, estimands, and replication path exceptionally clear. Original research articles must include a data-availability statement under the journal’s guidelines. [2]

## Novelty and framing risks

The central risk is that “benchmark” could be read as an evaluation paper with limited new theory or method, especially because the design deliberately excludes a successful neural benchmark, MCMC-derived joint L3 result, and full forecasting/TERGM/STERGM/RHEM analysis. JCSS’s consideration criteria require at least one new empirical/experimental result, new theoretical or methodological result, broad survey, or widely useful dataset/software introduction. The paper should explicitly claim a methodological result about how missingness mechanisms and conditional ERGM footprints alter the interpretation and ranking of directed link/hyperlink predictors—not merely report which score wins. [2]

A second risk is perceived incompleteness relative to contemporary link-prediction work. The recent JCSS link-prediction example foregrounds applied prediction, multiple ML models, and future-link estimation, while the paper here is intentionally static and comparative. The manuscript should pre-empt that comparison by defining its scope as a missingness-centred benchmark of interpretable structural baselines, explaining why neural/temporal models are outside the estimand, and avoiding claims about general forecasting superiority. [3]

A third risk is interdisciplinary accessibility. ERGM terminology, MPLE conditional footprints, dyadic versus hyperedge/event representations, and MNAR-out masking need a short conceptual bridge for readers outside statistical network methodology. The contribution should be tied to concrete social-science consequences: what conclusions about prospective ties become unreliable under each missingness mechanism, and when an ERGM structural baseline is a useful diagnostic. The journal’s scope and criteria emphasize accessibility as well as technical soundness. [1] [2]

## Recommendation

**Tentative target: submit to JCSS after framing revision.** Position the manuscript as a reproducible methodological benchmark for computational social-network analysis under observation failure, with ERGM as an interpretable structural benchmark—not as a claim to solve modern link prediction generally. Make the contribution, negative/limited results, and exclusion boundary explicit; include a prominent replication package and data-availability statement; and add a compact limitations/future-work paragraph covering temporal ERGM-family models and stronger neural baselines without implying that they were completed. This is an editorial-fit judgment only, not a prediction of acceptance probability; no acceptance-rate claim is made.

## References / direct-source citations

[1]: https://link.springer.com/journal/42001/aims-and-scope "Journal of Computational Social Science — Aims and scope"

[2]: https://link.springer.com/journal/42001/submission-guidelines "Journal of Computational Social Science — Submission guidelines"

[3]: https://link.springer.com/article/10.1007/s42001-024-00341-z "Identifying the factors influencing the development of bilateral investment treaties with health safeguards: a Machine Learning-based link prediction approach"

[4]: https://link.springer.com/article/10.1007/s42001-026-00471-6 "Influence disparity centrality: a new measure for identifying influential actors in social media networks"
