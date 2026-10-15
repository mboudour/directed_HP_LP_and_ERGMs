# Citation topic: ERGM foundations, change statistics, and conditional tie probabilities

**Scope.** These sources support the manuscript's formal, static ERGM machinery: exponential-family network distributions, toggle/change statistics, and dyad-level conditional tie probabilities. They do **not** support claims about neural benchmarks, MCMC-derived joint L3 evidence, missing-data mechanisms, or full temporal forecasting. The manuscript should describe any ERGM-derived score as a static conditional-footprint score unless it separately establishes an inferential or forecasting claim.

## Recommended sources

### 1. Wasserman and Pattison (1996)

**Citation.** Stanley Wasserman and Philippa Pattison. 1996. “Logit models and logistic regressions for social networks: I. An introduction to Markov graphs and *p*\*.” *Psychometrika* 61: 401–425. DOI: [10.1007/BF02294547](https://doi.org/10.1007/BF02294547). Publisher record: [SpringerLink](https://link.springer.com/article/10.1007/BF02294547).

**What it supports.** This is a foundational peer-reviewed source for the Markov-graph/*p*\* line of exponential-family network models and their logit interpretation. It supports a manuscript statement that ERGM foundations concern probability models for relational ties in which structural network tendencies are parameterized, and that local logit formulations arise from network dependence specifications. The publisher abstract explicitly describes Markov random graphs, extensions of these models, and approximate model fitting via the Strauss–Ikeda estimation strategy.

**Use boundary.** Cite it for historical/foundational ERGM or *p*\* context and logit interpretation, not as evidence that a particular directed link-prediction score is empirically superior, that MPLE is unbiased under MCAR/MNAR masking, or that the model forecasts future networks.

### 2. Krivitsky, Handcock, and Morris (2011)

**Citation.** Pavel N. Krivitsky, Mark S. Handcock, and Martina Morris. 2011. “Adjusting for Network Size and Composition Effects in Exponential-Family Random Graph Models.” *Statistical Methodology* 8(4): 319–339. DOI: [10.1016/j.stamet.2011.01.005](https://doi.org/10.1016/j.stamet.2011.01.005). Official author manuscript and bibliographic record: [PubMed Central, PMCID PMC3117581](https://pmc.ncbi.nlm.nih.gov/articles/PMC3117581/).

**What it supports.** This is the most direct citation for the manuscript's formal conditional-footprint construction. Section 3.1 defines a change statistic as the change in a network statistic when a dyad is toggled. The paper then derives the conditional probability of a tie given the rest of the network as the inverse-logit of the natural-parameter vector dotted with the change-statistic vector; its Appendix A.1 gives the dyad-conditional derivation. This supports notation and prose such as “the ERGM conditional tie probability is determined by the change statistics for the candidate dyad, conditional on the remaining network.” It is also suitable for explaining that the resulting local quantity is a conditional probability under a static ERGM, not automatically a temporal hazard or a missingness model.

**Use boundary.** The paper's motivating applications and asymptotic discussion concern network-size/composition effects, primarily in the standard binary-network ERGM setting. It does not validate a link-prediction benchmark, establish MNAR identification, or justify treating a conditional probability as a joint path/L3 probability. If the manuscript uses directed dyads, state the directed extension as a formal application of the dyad-toggle identity rather than claiming that this paper empirically validates the particular Enron or MathOverflow analysis.

### 3. Snijders, Pattison, Robins, and Handcock (2006)

**Citation.** Tom A. B. Snijders, Philippa E. Pattison, Garry L. Robins, and Mark S. Handcock. 2006. “New Specifications for Exponential Random Graph Models.” *Sociological Methodology* 36(1): 99–153. DOI: [10.1111/j.1467-9531.2006.00176.x](https://doi.org/10.1111/j.1467-9531.2006.00176.x). Publisher record: [Wiley Online Library](https://onlinelibrary.wiley.com/doi/10.1111/j.1467-9531.2006.00176.x).

**What it supports.** This canonical peer-reviewed source supports the ERGM foundation that static network structure can be represented with statistics producing dependence patterns such as transitivity and degree heterogeneity. Crucially for this manuscript, its abstract states that the proposed specifications are demonstrated for both graphs and **digraphs**, and it introduces geometrically weighted degree, alternating k-triangle, and alternating independent two-path statistics. It therefore supports careful language distinguishing native directed ERGM events/statistics from formal concepts imported into a directed candidate-edge score.

**Use boundary.** It supports model specification and directed-graph applicability, not the manuscript's masking design, event-first MCAR/MNAR comparisons, or claims about predictive accuracy. Its MCMC discussion is about approximate maximum-likelihood estimation for ERGMs; it should not be cited as evidence for “MCMC-derived joint L3 evidence” in this manuscript.

## Claim-to-source map

- **ERGM/*p*\* foundation and local logit interpretation:** Wasserman and Pattison (1996) [1].
- **Definition of a dyad toggle/change statistic:** Krivitsky, Handcock, and Morris (2011), §3.1 [2].
- **Conditional tie probability as inverse-logit of parameter-weighted change statistics:** Krivitsky, Handcock, and Morris (2011), §3.1 and Appendix A.1 [2].
- **Static structural dependence specifications and applicability to directed graphs/digraphs:** Snijders et al. (2006) [3].
- **What none of these sources establish:** neural baselines, missingness robustness under MCAR/MNAR, joint L3 evidence, or full temporal forecasting.

## References

[1]: https://doi.org/10.1007/BF02294547 "Wasserman and Pattison (1996), Logit models and logistic regressions for social networks"
[2]: https://doi.org/10.1016/j.stamet.2011.01.005 "Krivitsky, Handcock, and Morris (2011), Adjusting for Network Size and Composition Effects in Exponential-Family Random Graph Models"
[3]: https://doi.org/10.1111/j.1467-9531.2006.00176.x "Snijders, Pattison, Robins, and Handcock (2006), New Specifications for Exponential Random Graph Models"
