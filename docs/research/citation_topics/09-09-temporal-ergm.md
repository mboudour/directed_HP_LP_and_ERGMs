# Citation topic 09-09: Temporal ERGM and btergm methodology for the bounded chronological diagnostic

## Recommended sources

### [1] Leifeld, Philip, Skyler J. Cranmer, and Bruce A. Desmarais (2018)
**Temporal Exponential Random Graph Models with btergm: Estimation and Bootstrap Confidence Intervals.** *Journal of Statistical Software*, 83(6), 1–36. DOI: [10.18637/jss.v083.i06](https://doi.org/10.18637/jss.v083.i06). Official article record: [Journal of Statistical Software](https://www.jstatsoft.org/index.php/jss/article/view/v083i06); bibliographic record and abstract also verified in the [Penn State repository](https://pure.psu.edu/en/publications/temporal-exponential-random-graph-models-with-btergm-estimation-a/).

**What this source supports.** This is the direct methodological citation for a bounded chronological TERGM diagnostic implemented with `btergm`: TERGMs extend ERGMs to longitudinal network sequences, and the `btergm` implementation estimates a temporal ERGM by maximum pseudolikelihood and supplies bootstrap confidence intervals. The official abstract explicitly describes `btergm` as implementing bootstrap methods for a temporal ERGM estimated by maximum pseudolikelihood; the publisher record identifies the article as volume 83, issue 6, published 22 February 2018, pages 1–36, with the DOI above. It therefore supports wording such as: “As a bounded chronological diagnostic, we fit the specified TERGM/MPLE procedure to the ordered observed network snapshots and report the resulting coefficient/uncertainty or held-out diagnostic only within that observed temporal window.” It can also support a precise statement that this is a methodological diagnostic rather than a claim of a neural benchmark or an unrestricted forecasting system.

**What it does not support.** It does not establish MCAR or MNAR missingness assumptions, event-first masking, validity of Enron or MathOverflow as datasets, link-prediction superiority, or any particular local link score. It also does not justify claiming MCMC-derived joint L3 evidence: the cited article is specifically about `btergm`'s MPLE plus bootstrap workflow, not an MCMC joint-evidence result. Do not cite it for full forecasting beyond the bounded chronological diagnostic actually reported.

### [2] Hanneke, Steve, Wenjie Fu, and Eric P. Xing (2010)
**Discrete temporal models of social networks.** *Electronic Journal of Statistics*, 4, 585–605. DOI: [10.1214/09-EJS548](https://doi.org/10.1214/09-EJS548). Official record: [Project Euclid](https://projecteuclid.org/journals/electronic-journal-of-statistics/volume-4/issue-none/Discrete-temporal-models-of-social-networks/10.1214/09-EJS548.full).

**What this source supports.** This is the foundational peer-reviewed citation for the temporal ERGM idea itself. The official abstract states that the authors propose statistical models for network evolution over time as an extension of ERGMs, discuss their properties, adapt ERGM maximum-likelihood methods, and demonstrate hypothesis testing and classification. It supports defining the manuscript’s chronological diagnostic as a temporal extension of ERGM applied to an ordered sequence of network states, and supports distinguishing a temporal modeling diagnostic from a static, single-snapshot ERGM fit.

**What it does not support.** It does not support the manuscript’s missingness design (30 event-first MCAR and MNAR-out masks), a particular MPLE conditional-footprint score, directed hyperlink-prediction performance, neural baselines, MCMC-derived L3 evidence, or claims of full forecasting. Its examples and general framework should not be presented as validation of the manuscript’s Enron/MathOverflow results.

## Scope and claim discipline

Use [1] for the concrete `btergm`/MPLE/bootstrap implementation and [2] for the foundational temporal-ERGM formulation. Together they justify only a **bounded chronological diagnostic** over the manuscript’s ordered snapshots. They do not justify extending the results into a general missing-data theory, a benchmark against neural models, a joint MCMC L3 likelihood/evidence claim, or a full future forecasting claim. The manuscript should state its masking protocol, directed-event representation, and diagnostic horizon as its own design choices rather than attributing them to either source.

## Verification basis

Bibliographic fields and DOI for [1] were checked against the publisher’s Journal of Statistical Software record and the Penn State institutional repository. Bibliographic fields and DOI for [2] were checked against the Institute of Mathematical Statistics/Bernoulli Society’s Project Euclid record, which lists the authors, year, journal, volume, pages, DOI, and abstract.
