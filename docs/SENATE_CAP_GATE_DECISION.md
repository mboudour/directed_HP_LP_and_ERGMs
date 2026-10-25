# Senate native-event cap decision

## Decision

The primary Senate co-sponsorship native-event benchmark uses the fixed role cap

\[
|T| \leq 1, \qquad |H| \leq 10,
\]

without truncating any bill's original co-sponsor head. A bill with more than ten original co-sponsors is outside this capped primary target. The actor universe remains every distinct person with a Senate term overlapping the 118th Congress; people are never merged by Senate seat.

## Evidence considered

The decision follows the cap-first protocol in `docs/NETWORK_SCIENCE_POLITICAL_REPOSITIONING_PLAN.md`. The same 105-person universe, native-event construction, 30% MCAR mask rate, seed, candidate-locality rule, and 250,000-candidate concept budget were used throughout.

| Candidate head cap | Bill-record retention | Distinct event-type retention | Random-panel positive eligibility | Formal concepts with `|T|<=3` | M0/M4c MPLE pilot |
|---:|---:|---:|---:|---:|---|
| 3 | 68.038% | 61.793% | 668--669 of 672 per split | 0 | Not selected for the larger retention loss. |
| 5 | 78.144% | 73.903% | 801--803 of 803 per split | 0 | Not selected because it leaves the derived-concept target empty under the declared bounded enumeration. |
| 10 | 90.444% | 88.524% | 960--962 of 962 per split | 16 | All 3/3 M0 and M4c MPLE fits and conditional-score runs completed. |

At cap 10, the 16 formal concepts cover 251 of 5,619 full sponsor-to-co-sponsor arcs (4.467%). Thus formal concepts are retained as a deliberately small, derived comparison target. They are never interpreted as the recorded bills.

The cap-10 pilot's random panel contains 1,920--1,924 candidates and 960--962 positive types per split. The grammar-preserving sponsor-substitution panel contains 812--824 pairs. All cap-10 M0 and M4c maximum-pseudolikelihood fits and conditional score calculations completed across three matched MCAR pilot masks.

## Interpretation boundary

This selection concerns target definition and computational feasibility. The three pilot masks are not included in the primary 30-mask estimates or their uncertainty calculations. The primary benchmark uses a newly generated, independently seeded 30-mask MCAR/MNAR-out split set under the approved cap-10 policy.

## Reproducible evidence

- Event and actor policy: `docs/data_audits/senate_118_s_bills.md`.
- Retention and candidate profile: `results/phase2/senate_118_s_bills_cap_profile/summary.md`.
- Formal-concept feasibility: `results/phase2/senate_118_s_bills_cap_gate/summary.md`.
- Candidate pilots: `results/phase2/senate_118_s_bills_cap{3,5,10}_pilot_masks/` and `results/phase2/senate_118_s_bills_cap{3,5,10}_pilot_heuristics/`.
- Cap-10 ERGM fit and score pilot: `results/models/senate_118_s_bills_cap10_pilot_ergm_scores/`.
