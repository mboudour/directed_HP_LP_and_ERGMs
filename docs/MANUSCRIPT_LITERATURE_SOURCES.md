# Verified literature sources for Paper 1

This short source record supports the initial manuscript framing. It is not an
empirical evidence source: all reported benchmark findings must continue to
come from the published Phase 2 aggregate bundle.

1. **Link prediction.** Liben-Nowell and Kleinberg formalize link prediction
   as ranking unobserved future edges from a network snapshot and catalogue
   proximity scores including common neighbours and Adamic-Adar. This supports
   the paper's distinction between familiar dyadic LP rankings and the present
   missingness benchmark.
2. **ERGM conditional scores.** Hunter et al. explain that ERGM conditional tie
   probabilities are governed by change statistics with the remaining network
   held fixed; their discussion also motivates separating conditional scoring
   from simulation-based model checking. This supports the manuscript's MPLE
   conditional-score wording.
3. **Formal concepts.** Cordero et al. describe formal contexts, derivation
   operators, and concepts as closure/fixed-point pairs. This supports treating
   cap-first formal concepts as derived structural objects rather than as
   recorded event data.
4. **Relational hyperevents.** Lerner and Lomi model rates for sender-plus-
   receiver-set events and use Enron as an illustration. This supports the
   scope decision to defer event-level temporal forecasting and RHEM competition
   to the separate Paper 2 rather than treating them as missing Paper 1
   baselines.

## References

[1]: https://www.cs.cornell.edu/home/kleinber/link-pred.pdf "The Link Prediction Problem for Social Networks"

[2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC2743438/ "ergm: A Package to Fit, Simulate and Diagnose Exponential-Family Models for Networks"

[3]: https://journal.r-project.org/articles/RJ-2022-014/ "fcaR, Formal Concept Analysis with R"

[4]: https://academic.oup.com/jrsssa/article/186/3/577/6998599 "Relational Hyperevent Models for Polyadic Interaction Networks"
