# Citation topic: ERGM MPLE, MCMC estimation, degeneracy, and conditional-versus-joint interpretation

## Scope

These sources support only the manuscript’s **static ERGM estimation interpretation**: MPLE as a product of local conditional terms rather than the ERGM joint likelihood; MCMC-based maximum-likelihood estimation; and degeneracy/instability and its consequences for simulation and inference. They do **not** support claims about neural benchmarks, MCMC-derived joint L3 evidence, full forecasting, Enron or MathOverflow data provenance, or the manuscript’s 30 event-first MCAR/MNAR-out masks.

## Recommended sources

### 1. MPLE is a conditional/pseudolikelihood approximation, not the joint ERGM likelihood

**van Duijn, Marijtje A. J.; Gile, Krista J.; Handcock, Mark S. (2009).** “A Framework for the Comparison of Maximum Pseudo Likelihood and Maximum Likelihood Estimation of Exponential Family Random Graph Models.” *Social Networks*, 31(1), 52–62. DOI: **10.1016/j.socnet.2008.10.003**. Verified against the NLM/PMC author manuscript and publisher DOI record: https://pmc.ncbi.nlm.nih.gov/articles/PMC3500576/ ; https://doi.org/10.1016/j.socnet.2008.10.003

**Supports this manuscript claim:** The paper writes the ERGM conditional formulation and defines the pseudolikelihood as the product of those local conditional terms; it explains that the resulting MPLE is algebraically equivalent to a logistic-regression fit treating dyadic elements as independent observations. It explicitly distinguishes this local approximation from the full likelihood and states that, when dependence exists between edges, the MPLE approximation ignores that dependence, so MPLE estimates and standard errors can be suspect. This is the appropriate citation for describing a static ERGM MPLE “conditional footprint” as a collection of local conditional probabilities/scores, while warning that it is not a joint-probability score.

**Does not support:** A claim that a particular MPLE score is a calibrated probability for an unobserved directed edge; a claim that MPLE recovers the ERGM joint law; or any claim about link-prediction ranking under MCAR/MNAR missingness.

### 2. MCMC estimation and directed-graph convergence/degeneracy problems

**Snijders, Tom A. B. (2002).** “Markov Chain Monte Carlo Estimation of Exponential Random Graph Models.” *Journal of Social Structure*, 3(2), 1–40. DOI: **[empty: no DOI located in the official article record]**. Verified from the official Journal of Social Structure-hosted article PDF: https://www.cmu.edu/joss/content/articles/volume3/Snijders.pdf

**Supports this manuscript claim:** The article is an original treatment of frequentist MCMC estimation for exponential random graph (p*) models. Its abstract and methods describe Gibbs/Metropolis–Hastings simulation and Robbins–Monro likelihood-equation approximation. It explicitly treats directed graphs/digraphs and explains that some ERGM specifications produce bimodal or multimodal graph-density distributions; single-edge or small-step chains can then have extremely long sojourns in one region, making convergence slow and estimation unstable. It also distinguishes MCMC used to simulate from a fixed-parameter ERGM from MCMC procedures used repeatedly inside parameter estimation. This supports a careful statement that an ERGM fitted by MCMC-based likelihood estimation targets a **joint** model, but that this is not what an MPLE conditional-footprint score itself computes.

**Does not support:** Any claim that the present manuscript performed MCMC estimation, obtained joint L3 evidence, or conducted full temporal forecasting. It should be cited only as methodological background and as a warning about convergence/instability, not as evidence for the manuscript’s empirical results.

### 3. Formal instability/near-degeneracy and implications for MCMC/inference

**Schweinberger, Michael (2012 [online/published final record 2012]).** “Instability, Sensitivity, and Degeneracy of Discrete Exponential Families.” *Journal of the American Statistical Association*, 106(496), 1361–1370. DOI: **10.1198/jasa.2011.tm10747**. Verified against the NLM/PMC author manuscript, which reports the final journal citation and publisher DOI: https://pmc.ncbi.nlm.nih.gov/articles/PMC3405854/ ; https://doi.org/10.1198/jasa.2011.tm10747

**Supports this manuscript claim:** The paper formalizes instability in discrete exponential families and shows that unstable models are characterized by excessive sensitivity and near-degeneracy. It states that these properties obstruct MCMC simulation and statistical inference, and demonstrates that relational-data models with Markov dependence can be unstable. This is the strongest citation for qualifying ERGM interpretations with the model-degeneracy caveat: a fitted parameter vector or MLE does not by itself guarantee a practically useful, well-behaved distribution or reliable MCMC behavior.

**Does not support:** A blanket assertion that every ERGM is degenerate, a claim that the manuscript’s specific directed scores are degenerate, or empirical evidence about either dataset.

## Suggested manuscript wording boundary

Use the citations above to say that the reported ERGM baseline is a **static, conditional-footprint MPLE score** unless a full MCMC/MLE fit was actually performed. If discussing joint ERGM likelihood or model-based network simulation, cite Snijders (2002) and explicitly state that such joint inference is outside the reported bounded temporal diagnostic. Use Schweinberger (2012) for the qualification that instability/near-degeneracy can obstruct MCMC simulation and inference. Do not present any of these sources as validating the manuscript’s missingness masks, directed local-score definitions, or forecasting claims.

## Verification record

- van Duijn, Gile, and Handcock bibliographic metadata, pages, DOI, and the conditional-versus-joint MPLE discussion were checked in the PMC author manuscript and its publisher DOI link.
- Snijders title, author, date, method summary, directed-graph scope, and no-DOI status were checked in the official JOSS-hosted PDF. The source is a Journal of Social Structure article, not a placeholder or secondary summary.
- Schweinberger bibliographic metadata, final journal citation, DOI, and instability/near-degeneracy claims were checked in the PMC author manuscript and its publisher DOI link.
