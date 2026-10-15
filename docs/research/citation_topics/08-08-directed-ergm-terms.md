# Citation topic 08-08 — Directed ERGM reciprocity, degree, and triadic closure terms

## Recommended sources

### [1] Holland & Leinhardt (1981)

**Paul W. Holland and Samuel Leinhardt.** “An Exponential Family of Probability Distributions for Directed Graphs.” *Journal of the American Statistical Association* 76(373), 33–50 (1981). DOI: [10.1080/01621459.1981.10477598](https://doi.org/10.1080/01621459.1981.10477598). Publisher record: [Taylor & Francis](https://www.tandfonline.com/doi/abs/10.1080/01621459.1981.10477598).

The publisher’s abstract says that the paper develops an exponential family for directed (digraph) data, gives a substantive rationale, discusses special cases and interpretations, and describes an iterative-scaling fitting algorithm. This is the original directed p*/ERGM foundation. It supports the manuscript’s statement that a directed ERGM is a static exponential-family model for binary ordered ties and that directed local configurations can be represented as sufficient statistics. It is also the historically appropriate source for the directed reciprocity/mutuality tradition. Do **not** cite it for modern curved GW-degree or alternating-triad terms, or for the manuscript’s missingness experiments; those are not what the publisher abstract establishes.

### [2] Snijders, Pattison, Robins & Handcock (2006)

**Tom A. B. Snijders, Philippa E. Pattison, Garry L. Robins, and Mark S. Handcock.** “New Specifications for Exponential Random Graph Models.” *Sociological Methodology* 36(1), 99–153 (2006). DOI: [10.1111/j.1467-9531.2006.00176.x](https://doi.org/10.1111/j.1467-9531.2006.00176.x). Verified from the [University of Groningen research portal](https://research.rug.nl/en/publications/new-specifications-for-exponential-random-graph-models/) and [Crossref](https://api.crossref.org/works/10.1111/j.1467-9531.2006.00176.x).

The official record states that the paper proposes geometrically weighted degree distributions, alternating k-triangles, and alternating independent two-paths; it explicitly reports examples for graphs and digraphs. It supports claims that directed ERGMs can use degree-distribution terms and higher-order closure/transitivity statistics rather than naively relying on raw star and triangle counts, and that these are static structural specifications. It also supports careful language about ERGM estimation context and degeneracy. It does **not** support a claim that the manuscript performs MCMC-derived joint L3 inference, neural benchmarking, or full temporal forecasting.

### [3] Robins, Pattison & Wang (2009)

**Garry Robins, Pip Pattison, and Peng Wang.** “Closure, Connectivity and Degree Distributions: Exponential Random Graph (p*) Models for Directed Social Networks.” *Social Networks* 31(2), 105–117 (2009). DOI: [10.1016/j.socnet.2008.10.006](https://doi.org/10.1016/j.socnet.2008.10.006). Verified from the [Elsevier/ScienceDirect record](https://www.sciencedirect.com/science/article/abs/pii/S0378873308000592).

This is the most directly matched source for the directed terms. The publisher abstract says it proposes three directed triadic-closure parameters—cyclic effects, transitivity based on shared choices (activity), and transitivity based on shared popularity—and corresponding lower-order two-path connectivity effects. It also states that in- and out-degree distributions may be improved by star terms supplemented with isolated-node, source, sink, and mixed-star effects, and that goodness-of-fit diagnostics include density, reciprocity, degree distributions, and closure. Use it to support precise descriptions of directed triadic closure, in-/out-degree heterogeneity, and reciprocity as a reported network diagnostic. The source does **not** justify collapsing all directed triangles into one undifferentiated “triangle” term, nor does it support forecasting or missingness robustness claims.

## How these citations should be used in the manuscript

For a static ERGM conditional-footprint score, cite [1] for the directed exponential-family/digraph foundation, [2] for degree and higher-order transitivity specifications, and [3] for the directed distinction among cyclic closure, shared-choice/activity closure, shared-popularity closure, and in-/out-degree effects. State explicitly that the score is a conditional or pseudo-likelihood footprint of selected directed statistics, not evidence from a jointly sampled ERGM distribution. The sources support structural terminology and model specification only; they do not validate the manuscript’s 30 event-first MCAR/MNAR-out masks, Enron or MathOverflow results, or bounded temporal diagnostic.

## Verification note

Bibliographic fields were checked against publisher or institutional records. The Holland–Leinhardt record gives the title, authors, *JASA* volume/issue, pages 33–50, and DOI. The Groningen record and Crossref agree on the Snijders et al. title, authors, journal, volume 36(1), pages 99–153, year 2006, and DOI. The Elsevier record gives the Robins et al. title, authors, *Social Networks* volume 31(2), pages 105–117, year 2009, and DOI. No source is used here to claim a neural benchmark, MCMC-derived joint L3 evidence, or full forecasting.
