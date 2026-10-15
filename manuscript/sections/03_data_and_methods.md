# Data, targets, and benchmark design

## Target ladder

Let a directed relation be \(D=(V,A)\), where \(A\subseteq V\times V\)
contains no loops. A recorded directed group event is an ordered pair
\(e=(T,H)\) of non-empty, disjoint actor sets: the actors in \(T\) occupy the
tail role and those in \(H\) occupy the head role. Its dyadic footprint is
\(T\times H\). Aggregating records gives the directed graph whose arc set is
the union of their footprints.

The benchmark keeps three targets distinct. **Arc prediction** concerns a
missing dyad. **Native-event prediction** concerns a recorded ordered tail/head
event type. **Formal-concept prediction** concerns a maximal tail/head pair
derived from the aggregate relation by the predecessor-successor Galois
connection. A formal concept can have a footprint that largely agrees with
recorded-event footprints without being the same ordered group. This distinction
is empirical rather than merely terminological: Table 2 reports zero exact
concept/event matches in both primary native-event cores.

We enumerate concepts cap-first, retaining only pairs with \(|T|\leq 3\) and
\(|H|\leq 3\). The cap is an explicit representation and computing boundary.
It is not a claim that the retained concepts are all observed groups, and it is
not applied after an unbounded enumeration.

## Data eligibility and privacy

Table 1 records the study's dataset eligibility decisions. The primary
native-event analyses use two 100-node cores. The Enron core is a conservative
internal-custodian benchmark: it retains only complete records whose sender and
all To/Cc recipients have approved custodian mappings in the 1998–2002 interval.
It has 7,820 retained events and 635 static directed arcs. This is not a claim
to represent the complete Enron communication system.

The MathOverflow core represents a different role structure. A native event is
a declared-window set of distinct answerers in the tail and the question asker
in the head. Its reconstruction policy, including the answer window and
handling rules, is frozen before the benchmark. It is therefore a reconstructed
native-event target, not an email analogue.

EU-core is retained for a bounded directed-dyadic chronological diagnostic.
CAVIAR is retained only as a full static directed-matrix, dyadic/footprint
analysis. Ciel lacks source-specific direction evidence, and Jmail remains
admissibility-pending; neither contributes a substantive result. All manuscript
inputs are aggregate-only. Raw archives, email content, email addresses,
identity maps, candidate-level scores, and per-event predictions are excluded.

## Missingness design

The primary unit of missingness is a distinct ordered tail/head native-event
type. When a type is selected, every repeated record of that type is withheld,
and the observed graph is rebuilt from the remaining types. Thus an observed
footprint of a held-out event is not leakage: a different observed event type
may induce the same dyads.

For each native-event core, the primary analysis fixes 30 MCAR masks and 30
MNAR-out masks at nominal type-level rate 0.30. MCAR uses fixed-count sampling.
MNAR-out is the predeclared oracle inclusion mechanism that favours types
associated with high-activity senders; its realised type rate can therefore vary
slightly. Because the same nominal type rate can remove different numbers of
records and projection arcs, all mask descriptions retain type-, record-, and
arc-level realised loss. MNAR-in and the rate grid are supplementary analyses,
not a replacement for the two primary mechanisms.

## Candidate panels and evaluation tasks

The random native-event panel contains held-out types and true non-event
negatives matched exactly on tail and head arity. Candidate participants must
be within weak distance two in the split-specific observed projection. Observed
and held-out event types are excluded from the negative pool. The random panel
therefore evaluates ranking in a defined, balanced, arity-matched
case-control universe; its PR-AUC is not a calibrated probability at natural
prevalence.

Two hard panels impose directional alternatives. The reversal/orientation panel
compares \((T,H)\) with its unobserved reversal \((H,T)\). The role-exchange
panel swaps one tail actor and one head actor while preserving the actor set and
both role arities. A fixed-role-assignment task provides the known participants
and the true arities, then asks the score to rank compatible role partitions.
No unavailable hard case is replaced by an easier random negative.

## Directed scores and ERGM benchmark

The heuristic branch lifts dyadic directed scores over a candidate footprint.
It includes reverse-arc, degree-product, directed common-neighbour, and
Adamic-Adar components. These are uncalibrated rankings, so the native-event
analysis reports ranking metrics rather than accuracy, F1, or log loss.

For each frozen split, the ERGM branch fits the designated directed static
specifications only to the observed projection using MPLE. The reported
single-dyad values are exact conditional pseudolikelihood scores under the
fitted model. Candidate footprints are summarized by `L1` (arithmetic mean),
`L1g` (geometric mean), and factorized `L2` (product). These are not the same
object as a jointly simulated footprint probability. In particular, the
factorized `L2` does not impose one shared observation constraint on every
unknown candidate dyad.

The predeclared primary ERGM comparison is `M4c::L1g` against `M0::L1` on the
random native-event panel. `M0` is the density reference. `M4c` adds directed
mutuality, degree, closure, and cyclic structure in the stated MPLE ladder. The
comparison tests conditional-score discrimination in the frozen-mask candidate
panel; it does not estimate an event-generating probability or establish ERGM
coefficient inference.

## Paired uncertainty and chronological boundary

For the primary 30-mask branches, uncertainty is calculated by resampling whole
frozen masks within dataset: 10,000 percentile-bootstrap draws give 95%
intervals, and 20,000 paired sign-flip draws give two-sided reference
contrasts. Mask replicates are not treated as independent networks, and no
cross-network pooling is performed.

The temporal work is restricted to a chronological diagnostic on Enron and
EU-core. Factorized lagged score models and a small btergm MPLE ladder compare
history-only and history-plus-contemporaneous specifications over two response
transitions. They do not provide a rolling-origin forecast evaluation, a joint
temporal probability, or a STERGM/RHEM comparison. Those questions are
explicitly deferred to the separate forecasting paper.
