# Conditional ERGM simulation sources

This source note supports the Phase 2 implementation of the plan's static joint
footprint score \(L3\)-F. It is not a results document.

- The agreed paper plan defines \(L3\)-F as
  \(P_{\hat\theta}(T\times H\subseteq A\mid O)\), estimated by conditional
  ERGM simulations. In every simulated completion, the footprint-complete
  indicator is averaged and its Monte Carlo standard error is reported. It
  defines the dependence increment as \(\log L3\text{-F}-\log L2\).
  The applicable plan is the project-local uploaded document.
- Statnet documents the `observed` constraint as preserving observed dyads of
  the given network. The advanced ERGM workshop specifies that it restricts
  proposals to dyads recorded as missing. Therefore a candidate-specific
  simulation can fix every training-network dyad except the candidate's
  unobserved footprint dyads.
- The `network` package uses its mandatory edge `na` attribute to mark a dyad
  as missing. Its documented example sets a row of directed dyads to `NA` with
  `network[i, , add.edges = TRUE] <- NA`. The implementation will mark only
  candidate footprint dyads absent from the event-first observed projection as
  `NA`; arcs already observed through another event remain fixed at one.
- A missing-network ERGM paper demonstrates conditional ERGM simulation with
  `constraints = ~observed`; this confirms the simulation pattern but does not
  determine the present paper's masking/estimation design.

## Sources

1. https://statnet.org/workshop-advanced-ergm/advanced_ergm_tutorial.html
   — Statnet advanced ERGM workshop; sample-space constraints and the `observed`
   observation constraint.
2. https://github.com/statnet/network/blob/master/R/access.R
   — `network` source and documentation for `network.naedgecount`, missing-edge
   representation, and `network[i, , add.edges = TRUE] <- NA`.
3. https://github.com/statnet/ergm/blob/master/R/simulate.R
   — `simulate.ergm` implementation; accepts a `basis` network and constraints.
4. https://pmc.ncbi.nlm.nih.gov/articles/PMC4743534/
   — Wang et al., *Multiple Imputation for Missing Edge Data: A Predictive
   Evaluation Method for Network Analysis*; example conditional ERGM simulation
   with `constraints = ~observed`.
