# Citation topic 10-10: Relational event and relational hyperevent models for deferred forecasting context

## Recommended sources

### [1] Butts (2008)

- **Authors:** Carter T. Butts
- **Year:** 2008
- **Title:** *A Relational Event Framework for Social Action*
- **Venue:** *Sociological Methodology*, 38(1), 155–200
- **DOI:** [10.1111/j.1467-9531.2008.00203.x](https://doi.org/10.1111/j.1467-9531.2008.00203.x)
- **Verified source:** [SAGE publisher record](https://journals.sagepub.com/doi/10.1111/j.1467-9531.2008.00203.x)
- **Source type:** Original peer-reviewed methodological article.
- **What it supports:** Use this source for the foundational definition and scope of a relational event model (REM): actions are discrete events in which an actor directs behavior toward one or more entities; the framework models event histories with likelihood-based inference and history-dependent mechanisms such as activity, recency, persistence, preferential attachment, and transitive/cyclic interaction. It also supports the manuscript's distinction between native event-first temporal modeling and a static graph score: REM is formulated around an observed event history (or event sequence), not merely a single aggregated adjacency matrix.
- **What it does not support:** It does not support claims about neural models, missing-data masks, MCAR/MNAR inference, ERGM MPLE, MCMC joint evidence, or a complete forecasting benchmark. In this manuscript it should be cited only for REM's event-history formalism and as deferred temporal context.

### [2] Perry and Wolfe (2013)

- **Authors:** Patrick O. Perry and Patrick J. Wolfe
- **Year:** 2013
- **Title:** *Point process modelling for directed interaction networks*
- **Venue:** *Journal of the Royal Statistical Society: Series B (Statistical Methodology)*, 75(5), 821–849
- **DOI:** [10.1111/rssb.12013](https://doi.org/10.1111/rssb.12013)
- **Verified source:** [Wiley/Royal Statistical Society publisher record](https://rss.onlinelibrary.wiley.com/doi/10.1111/rssb.12013)
- **Source type:** Original peer-reviewed methodological article.
- **What it supports:** Use this source for the directed-event point-process context: repeated sender–receiver interactions are represented over time as a multivariate point process, with a Cox multiplicative intensity whose covariates depend on process history; the paper explicitly asks which traits and behaviors are predictive of interaction and applies the model to corporate email. This is the closest canonical citation for a bounded deferred-forecasting interpretation of directed event scores: a history-conditioned event-rate/intensity perspective, rather than a static link score.
- **What it does not support:** It does not establish the manuscript's MCAR/MNAR masking protocol, its particular local link-prediction scores, static ERGM MPLE conditional-footprint scores, or any claim of full out-of-sample forecasting performance. It also should not be used to imply a neural benchmark or MCMC-derived joint L3 evidence.

### [3] Lerner and Lomi (2023)

- **Authors:** Jürgen Lerner and Alessandro Lomi
- **Year:** 2023
- **Title:** *Relational hyperevent models for polyadic interaction networks*
- **Venue:** *Journal of the Royal Statistical Society Series A: Statistics in Society*, 186(3), 577–600
- **DOI:** [10.1093/jrsssa/qnac012](https://doi.org/10.1093/jrsssa/qnac012)
- **Verified source:** [Oxford Academic/Royal Statistical Society publisher record](https://academic.oup.com/jrsssa/article/186/3/577/6998599)
- **Source type:** Original peer-reviewed methodological article.
- **What it supports:** Use this source for the relational hyperevent model (RHEM) extension. The paper defines polyadic or multicast interactions as one sender addressing multiple receivers simultaneously and specifies event rates using hyperedge covariates for the sender and the entire receiver set, rather than only dyadic sender–receiver covariates. It compares dyadic REM and RHEM and illustrates the distinction on the Enron email data. This supports a careful statement that RHEM is relevant deferred temporal context when an email/message event can have a receiver set, including higher-order receiver-set dependence.
- **What it does not support:** The paper is not a missingness paper and does not validate the manuscript's 30 event-first MCAR/MNAR-out masks, MathOverflow analysis, static ERGM MPLE scores, neural baselines, MCMC joint L3 evidence, or full forecasting claims. Its Enron analysis is an explanatory model comparison on event data, not evidence that the manuscript's bounded diagnostic is a forecasting benchmark.

## Recommended manuscript use

Cite [1] for the native REM/event-history concept, [2] for directed history-conditioned point-process/intensity context and the limited predictive interpretation of event rates, and [3] only when discussing the formal polyadic/hyperevent extension. The manuscript should state explicitly that these sources provide **deferred forecasting context**, not a claim that the present study fits REM/RHEM, performs full temporal forecasting, or benchmarks neural predictors. The RHEM citation is especially appropriate for terminology and formal contrast: a receiver set is a hyperedge-level object, whereas a directed dyadic link score is a different object.

## Verification and limitations

Bibliographic metadata were checked against publisher pages. The first source gives the article title, author, *Sociological Methodology* volume/issue, pages 155–200, publication year, and DOI. The second gives authors, title, *JRSS Series B* volume/issue, pages 821–849, publication date/year, DOI, and its point-process abstract. The third gives authors, title, *JRSS Series A* volume/issue, pages 577–600, DOI, and its abstract/conclusion describing RHEM and the Enron illustration. No source is being used here to support missingness assumptions, ERGM estimation, neural benchmarking, MCMC evidence, or unrestricted forecasting.
