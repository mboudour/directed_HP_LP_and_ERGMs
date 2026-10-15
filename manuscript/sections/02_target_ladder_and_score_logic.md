# Targets and score logic

## From events to footprints and concepts

For an observed directed relation \(D=(V,A)\), a native event is an ordered
pair \(e=(T,H)\), where \(T\) and \(H\) are non-empty, disjoint actor sets.
Its directed two-section footprint is

\[
\pi(e)=T\times H.
\]

If \(\mathcal E\) is an event collection, aggregation yields
\(A=\bigcup_{e\in\mathcal E}\pi(e)\). This map is many-to-one. Distinct event
collections can induce the same directed graph, and a graph alone cannot
generally identify which event collection produced it.

Formal concepts offer one reproducible structural section of the aggregate
relation. For \(X,Y\subseteq V\), define common successors and predecessors
by

\[
X^{\uparrow}=\{v:(x,v)\in A\ \text{for every }x\in X\},\qquad
Y^{\downarrow}=\{u:(u,y)\in A\ \text{for every }y\in Y\}.
\]

A formal concept is a fixed pair \((T,H)\) with
\(T^{\uparrow}=H\) and \(H^{\downarrow}=T\). Equivalently, it is a maximal
complete tail-head rectangle in the adjacency relation. It is a property of the
aggregate graph, whereas a native event is a property of the record stream. The
benchmark therefore evaluates the two targets separately.

## Directed local scores and an ERGM conditional score

Let \(N^+(i)\) and \(N^-(i)\) denote the observed successors and predecessors
of actor \(i\). The three directed common-neighbour components used in the
benchmark are

\[
 s^{OI}_{ij}=|N^+(i)\cap N^-(j)|,\qquad
 s^{OO}_{ij}=|N^+(i)\cap N^+(j)|,\qquad
 s^{II}_{ij}=|N^-(i)\cap N^-(j)|,
\]

with total \(s^{CN}_{ij}=s^{OI}_{ij}+s^{OO}_{ij}+s^{II}_{ij}\). The same
roles are used by the directed Adamic-Adar variants, with each common neighbour
weighted by its observed total degree.

For a transitive-triple statistic that counts ordered triples
\(a\to b\to c\) with shortcut \(a\to c\), toggling arc \(i\to j\) changes the
statistic by \(s^{CN}_{ij}\). The new arc can act as the shortcut, the first
leg, or the second leg, yielding the OI, OO, and II terms respectively. Thus an
ERGM containing only an edge term and this transitive-triple statistic has a
conditional log-odds that is an affine function of total directed common
neighbours. This is an arc-level relationship. It does not imply that a lifted
higher-order candidate score is identical across methods.

For an ERGM with statistic vector \(g(Y)\), the conditional tie score is

\[
 p_{ij}=\Pr_\theta(Y_{ij}=1\mid Y_{-ij})
 =\operatorname{logit}^{-1}\{\theta^\top\Delta_{ij}g(Y)\}.
\]

In this paper, \(p_{ij}\) is estimated through the split-specific MPLE fit and
used as a conditional score. It is not presented as an MCMC-validated marginal
probability.

## Footprint aggregation and the dependence boundary

For a candidate \(e=(T,H)\), define three score summaries over its footprint:

\[
L_1(e)=\frac{1}{|T||H|}\sum_{t\in T}\sum_{h\in H}p_{th},\qquad
L_{1g}(e)=\left(\prod_{t\in T}\prod_{h\in H}p_{th}\right)^{1/(|T||H|)},
\]

and the factorized product

\[
L_2^{\mathrm{fac}}(e)=\prod_{t\in T}\prod_{h\in H}p_{th}.
\]

`L1` is an arithmetic footprint average and `L1g` is a size-normalized
geometric average. The factorized product is sensitive to footprint size. None
of these quantities is automatically the probability that all footprint arcs
are present jointly. A joint quantity would require all unknown candidate arcs
to be placed under a shared observation constraint and evaluated from the
corresponding joint conditional distribution.

This distinction sets the dependence boundary of the paper. The primary results
use `L1`, `L1g`, and factorized `L2` as conditional-pseudolikelihood score
constructions. A successful MCMC-derived higher-order joint score is not
available for the primary Enron model ladder. The manuscript consequently does
not use an observed gap between `L2` and a simulation score as a substantive
primary dependence estimate.

## Bounded temporal implication

When every temporal predictor is a function only of a previous network window,
the resulting next-window dyad scores factorize conditional on that history.
Within-window dependence enters only when terms are evaluated on the response
window itself. This paper uses that observation to organize a bounded
history-versus-contemporaneous diagnostic. It does not convert the benchmark
into a native-event forecasting analysis.
