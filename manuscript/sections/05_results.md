# Results

## Formal concepts preserve footprints without recovering recorded events

The cap-first concept sections have different coverage profiles in the two
primary cores. Enron contains 232 capped formal concepts over 635 static arcs;
MathOverflow contains 207 over 1,020 arcs. The critical comparison is not the
number of concepts but their relation to recorded group events (Table 2).

Neither core contains an exact tail/head match between a capped formal concept
and a native-event type. Concept precision and native-event-type recall are both
zero. Yet the footprint Jaccard is 0.8567 in Enron and 0.6634 in MathOverflow.
In Enron, concepts cover 86.62% of the native-event footprint arcs, while native
events cover 98.73% of the concept footprint arcs. The corresponding quantities
for MathOverflow are 66.47% and 99.70%.

This contrast is central to the benchmark. The aggregate graph retains enough
shared dyadic structure for a concept section to overlap strongly with event
footprints, but it does not identify the observed ordered group. Concept
recovery and native-event recovery are therefore reported as different targets.
The result does not license the interpretation of a formal concept as a
reconstructed email or question-answering event.

## Random native-event panels show conditional-score gains

Table 3A reports selected predeclared random-panel rows from 30 frozen masks
per dataset and primary missingness mechanism. The constant-density ERGM
reference `M0::L1` has PR-AUC 0.5000 on every balanced random panel. The
higher-order conditional-footprint score `M4c::L1g` reaches 0.8584 and 0.8324
in the Enron MCAR and MNAR-out panels, and 0.7396 and 0.7394 in the
MathOverflow MCAR and MNAR-out panels.

The directed heuristic patterns differ across the two interaction settings. In
Enron, total directed Adamic-Adar has PR-AUC 0.7966 under MCAR, whereas the
reverse-arc mean is stronger under MNAR-out (0.7761 versus 0.7472). In
MathOverflow, total directed Adamic-Adar has PR-AUC 0.7589 under MCAR and
0.7593 under MNAR-out, while the reverse-arc score is near the balanced-panel
reference. These results are descriptive comparisons of fixed, arity-matched
candidate panels rather than calibrated prevalence claims.

The predeclared paired ERGM contrast confirms the random-panel separation
within each fixed network (Table 4). Relative to `M0::L1`, `M4c::L1g` raises
PR-AUC by 0.3584 in Enron under MCAR (95% percentile-bootstrap interval
0.3519–0.3648) and 0.3324 under MNAR-out (0.3269–0.3379). The corresponding
MathOverflow differences are 0.2396 (0.2305–0.2485) and 0.2394
(0.2303–0.2484). Every paired sign-flip calculation attains the 20,000-draw
Monte Carlo lower resolution, 1/20,001. These intervals and p-values quantify
variation across the 30 frozen missingness realizations in a fixed dataset; they
are not cross-network or population inference.

## Directional hard panels qualify random-panel conclusions

The hard panels hold the actor set or an oriented alternative much closer to the
positive than the random panel does (Table 3B). Therefore they test a different
claim: whether scores retain information about a directed event's roles after
simple footprint completion is no longer sufficient.

In Enron, the `M4c::L1g` PR-AUC is near the balanced reference under MCAR for
both reversal/orientation (0.4899) and role exchange (0.4969). Under MNAR-out,
the same score rises modestly to 0.5575 and 0.5423, and the reverse-arc mean is
similarly directional (0.5685 and 0.5515). Thus the Enron random-panel lift
does not transfer to a stable directional-event recovery result.

MathOverflow has a different hard-panel profile: `M4c::L1g` is above the
balanced reference in both mechanisms and both panels, ranging from 0.6115 to
0.6543. However, its score level and the heuristic ordering are target- and
dataset-specific, rather than uniform consequences of random-panel performance.
The evidence supports the narrower conclusion that a directional test can alter
both performance level and ordering. It does not justify a single model as a
universal role-recovery method.

The role-assignment results reinforce this distinction (Table 3C). With the
participants and role arities supplied, Enron's reverse-arc mean has weighted
top-1 accuracy 0.6012 under MCAR and 0.6541 under MNAR-out, while MathOverflow
is better ranked by degree-product mean (0.7817 and 0.7521). The role task does
not use random case-control prevalence and is not interchangeable with the
random or hard panel metrics.

## The chronological analysis remains a bounded diagnostic

Table 5 records the status of the temporal checks. In both Enron and EU-core,
all three factorized lagged models completed over two response transitions. The
small btergm MPLE ladder completed through `T1` for Enron, while its
contemporaneous `T2` and `T2_minus_H` specifications had non-finite
coefficients. The EU-core btergm branch produced finite statuses for the
listed models, still using only two response panels and 20 bootstrap
replicates.

These outputs make the intended conceptual distinction observable: a lagged
score is conditional on history, whereas a contemporaneous conditional score
uses within-window structure. They do not yield a same-design forecast contest,
temporal simulation result, or evidence about formation and dissolution.
Accordingly, the chronological material is retained as a diagnostic and not
used to enlarge the paper's central missingness claim.

## Explicit exclusions protect the claim boundary

Table 6 records the gates that constrained the final evidence set. Higher-order
MCMC estimation did not satisfy the Enron feasibility gate, so there is no
primary MCMC-derived joint `L3` result. The official NHP-D reproduction gate
did not supply a defensible directed neural benchmark. Regime K,
masking-plus-forecasting, STERGM, RHEM, and rolling-origin native-event
forecasting are outside this paper. These are substantive scope controls rather
than unreported negative results.
