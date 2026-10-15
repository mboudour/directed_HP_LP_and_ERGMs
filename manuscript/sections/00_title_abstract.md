# Title and abstract

## Working title

**Exponential Random Graph Models as a Benchmark for Directed Link and Hyperlink Prediction under Missingness**

## Abstract

Directed interaction data can be evaluated at several non-equivalent levels: the
dyadic arcs induced by records, algebraically derived directed groups, and the
recorded ordered groups themselves. We develop a missingness-centred benchmark
that keeps these targets separate and compares directed link-prediction scores
with conditional scores from a directed exponential random graph model (ERGM).
The primary design uses event-first masking of ordered tail/head event types on
a strict Enron custodian core and a reconstructed MathOverflow interaction core.
Each dataset has 30 fixed masks under MCAR and activity-biased MNAR-out
missingness. Random arity-matched panels, directional hard panels, and fixed
role-assignment tasks distinguish footprint completion from recovery of event
orientation. On random native-event panels, the predeclared `M4c::L1g` ERGM
conditional-footprint score exceeded the density reference `M0::L1` in PR-AUC
by 0.3584 (95% bootstrap interval 0.3519–0.3648) and 0.3324
(0.3269–0.3379) for Enron under MCAR and MNAR-out, and by 0.2396
(0.2305–0.2485) and 0.2394 (0.2303–0.2484) for MathOverflow. These are
within-network, matched-mask comparisons. Formal concepts did not exactly match
any native-event type in either core, despite footprint Jaccards of 0.8567
(Enron) and 0.6634 (MathOverflow). Thus, good dyadic-footprint completion does
not establish recovery of an observed directed group. The paper reports a
bounded chronological diagnostic but does not claim forecasting, a neural
benchmark, or an MCMC-derived higher-order joint ERGM result.

**Keywords:** directed networks; hyperlink prediction; exponential random graph
models; network missingness; formal concepts; native events
