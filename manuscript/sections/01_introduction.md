# Introduction

A missing directed interaction can be interpreted in more than one way. At the
most familiar level, the task is to rank absent dyads in an observed graph.
Classical link prediction treats this as a topology-based ranking problem and
uses proximity measures such as common neighbours and Adamic-Adar [1]. But many
directed records are not inherently dyadic. An email has a sender and a recipient
set; a question-answering exchange can have a set of answerers and one asker. If
such records are aggregated into directed arcs, the aggregate preserves some
footprints of an event while discarding much of its group and role identity.

This paper studies that distinction under missingness. It asks how directed link
prediction, directed hyperlink prediction, and ERGM conditional scores relate
when the intended target is made explicit. The problem is not to introduce a
new universal predictor. It is to build a reproducible benchmark that stops a
strong dyadic result from being misread as recovery of an observed directed
group.

ERGMs provide a useful statistical comparator because their conditional tie
probabilities are functions of model change statistics with the rest of the
network held fixed [2]. This makes it possible to compare a local directed score
with an ERGM conditional score on the same masked graph. It does not imply that
an MPLE fit supplies a joint probability for a multi-dyad event footprint.
Jointness requires an additional conditioning and simulation argument, whose
feasibility must be demonstrated rather than presumed.

The paper also distinguishes recorded groups from formal concepts. In formal
concept analysis, derivation operators identify closure pairs in a binary
relation [3]. Applied to a directed aggregate graph, these pairs yield
maximal tail/head structures and are legitimate structural targets. They are
not automatically the recorded events that generated the relation. The empirical
fidelity audit in this paper makes that non-identifiability visible rather than
assuming it away.

The project continues the missingness-centred comparison of LP, HP, and ERGM
estimation in the author's accepted undirected-network study. Direction changes
both the data-generating record and the evaluation problem: tails and heads have
different roles, missingness can target outgoing activity, and a reversal or
role-exchange negative can be much harder than a random non-event. The primary
analysis therefore uses event-first masks and reports random, hard, and
role-assignment evaluations separately.

The contribution is fourfold. First, the benchmark formalizes a target ladder
among dyadic footprints, formal concepts, and native events. Second, it compares
directed heuristics and split-specific ERGM conditional-footprint scores under
the same frozen missingness realizations. Third, it shows why strong footprint
overlap and random-panel ranking do not by themselves identify a recorded group
or its tail/head roles. Fourth, it preserves a narrow chronological diagnostic
without recasting the paper as a forecasting contest.

That last boundary matters. Models designed for time-ordered polyadic events,
such as relational hyperevent models, directly represent a sender and a receiver
set and are appropriate competitors for a full event-forecasting study [4].
Such a study would require rolling origins, a forecasting horizon, and a
formation/persistence design. Those choices belong to the planned second paper.
Here the contribution remains a static missingness benchmark with a bounded
temporal check.

## References

[1]: https://www.cs.cornell.edu/home/kleinber/link-pred.pdf "The Link Prediction Problem for Social Networks"

[2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC2743438/ "ergm: A Package to Fit, Simulate and Diagnose Exponential-Family Models for Networks"

[3]: https://journal.r-project.org/articles/RJ-2022-014/ "fcaR, Formal Concept Analysis with R"

[4]: https://academic.oup.com/jrsssa/article/186/3/577/6998599 "Relational Hyperevent Models for Polyadic Interaction Networks"
