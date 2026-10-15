# Citation topic: network missing data, sampling, and MCAR/MAR/MNAR mechanisms

**Scope.** These sources support the manuscript's missingness vocabulary and its event-first masking design. They do not support claims about neural benchmarks, MCMC-derived joint L3 evidence, or full forecasting. The manuscript should describe its 30 MCAR and MNAR-out masks as controlled missingness experiments, not as an empirical identification of how Enron or MathOverflow data went missing.

## Recommended sources

### [1] Rubin (1976)

Donald B. Rubin (1976), “Inference and missing data,” *Biometrika*, 63(3), 581–592. DOI: [10.1093/biomet/63.3.581](https://doi.org/10.1093/biomet/63.3.581). Verified against the Oxford Academic publisher record, which gives the author, title, volume/issue, pages, publication date (1 December 1976), and DOI.

**What it supports.** Use this original paper for the manuscript's formal statistical language about missing-data mechanisms and ignorability. Rubin states conditions under which the missingness process can be ignored for likelihood or Bayesian inference: missing at random plus a distinct missingness-process parameter (and, for sampling-distribution inference, the relevant observed-at-random condition). This is the appropriate citation for defining MCAR/MAR/MNAR terminology and for warning that treating the observation process as ignorable requires assumptions. It supports a methodological caveat around comparing scores after masking; it does **not** by itself establish that a particular network mask is MAR or MNAR, nor does it provide a network-specific sampling result.

### [2] Kossinets (2006)

Gueorgi Kossinets (2006), “Effects of missing data in social networks,” *Social Networks*, 28(3), 247–268. DOI: [10.1016/j.socnet.2005.07.002](https://doi.org/10.1016/j.socnet.2005.07.002). Verified against the Elsevier/ScienceDirect publisher record, which gives the title, author, journal, volume/issue, pages, date (July 2006), and DOI.

**What it supports.** Use this network-specific simulation study for the claim that missing actors, affiliations/edges, survey non-response, boundary specification, and degree-censored fixed-choice designs can substantially change observed network-level structure. Its abstract reports sensitivity analyses on a scientific collaboration network and random bipartite graphs, with direction-dependent effects on clustering and assortativity. This supports motivating event/edge masking as a measurement-sensitivity problem and warning that network statistics can be biased under sampling and non-response. It does **not** establish MCAR/MAR/MNAR labels for the manuscript's masks, does not study Enron or MathOverflow, and does not validate directed hyperlink prediction or temporal forecasting.

### [3] Huisman (2009)

Mark Huisman (2009), “Imputation of missing network data: Some simple procedures,” *Journal of Social Structure*, 10(1), 1–29. DOI: **none located in the publisher/author records checked**. Verified against the University of Groningen research portal (peer-reviewed article record, journal/volume/issue/year, 29 pages, author manuscript) and the official Carnegie Mellon-hosted *Journal of Social Structure* PDF. Crossref title searching did not return a DOI for this 2009 journal article; the DOI sometimes displayed by third-party index pages belongs to a later record and is not used here. Official links: [University of Groningen record](https://research.rug.nl/en/publications/imputation-of-missing-network-data-some-simple-procedures/) and [journal PDF](https://www.cmu.edu/joss/content/articles/volume10/huisman.pdf).

**What it supports.** Use this source for the particularly relevant directed-network missingness evidence. Huisman's simulation study examines missing actors (unit non-response) and missing ties (item non-response), including a random mechanism and two non-random mechanisms related to actor/network characteristics; the paper reports that ignoring missingness can strongly distort structural properties and that effects differ between directed and undirected graphs. This supports the manuscript's justification for separate MCAR-style and outcome/edge-dependent MNAR-out masks, and for reporting masking effects rather than assuming complete-case behavior is unbiased. It does **not** justify calling every outcome-dependent mask “MNAR” in Rubin's formal sense without specifying the full-data and observation models; it is a network simulation study, not a proof of ignorability or a study of the two target datasets.

## Manuscript-use note

A precise framing is: Rubin [1] supplies the formal mechanism vocabulary and ignorability warning; Kossinets [2] supplies network sampling/missingness sensitivity evidence; Huisman [3] supplies directed-network and tie/actor non-response evidence. The manuscript may therefore state that its MCAR and MNAR-out masks are **design-based stress tests under named assumptions**. It should avoid claiming that the observed data-generating process is known to be MCAR, MAR, or MNAR, and should distinguish missingness of an observed event/link from a future-link prediction target. The bounded temporal diagnostic remains a diagnostic only, not a full forecast.

## Verification links

- [Oxford Academic publisher record for Rubin (1976)](https://doi.org/10.1093/biomet/63.3.581)
- [Elsevier/ScienceDirect publisher record for Kossinets (2006)](https://www.sciencedirect.com/science/article/abs/pii/S0378873305000511)
- [University of Groningen author/institution record for Huisman (2009)](https://research.rug.nl/en/publications/imputation-of-missing-network-data-some-simple-procedures/)
- [Official Journal of Social Structure PDF mirror for Huisman (2009)](https://www.cmu.edu/joss/content/articles/volume10/huisman.pdf)
