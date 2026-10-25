# U.S. Senate 118th Congress S. bill co-sponsorship audit

## Event definition

One source record is a Senate bill (`S.`) from the 118th Congress. Its singleton tail is the Bill Status sponsor Bioguide ID; its head is the set of co-sponsors whose `isOriginalCosponsor` field is `True`. The target retains an original co-sponsor even if the official record later lists a withdrawal date, because it represents the coalition recorded at introduction.

## Source accounting

- Official XML files read: `5,649`
- Valid records with a nonempty original-co-sponsor head: `4,374`
- Measures with zero original co-sponsors: `1,275`
- Records excluded for non-single/missing sponsors: `0`
- Records excluded for an invalid introduction date: `0`
- Original-cosponsor withdrawal entries retained as introduction-time members: `6`

## Actor-universe comparison

| Policy | Nodes | Valid events retained | Event retention | Static arcs |
|---|---:|---:|---:|---:|
| reference_date_2024_01_01 | 100 | 4,170 | 95.336% | 5,209 |
| all_serving_persons_during_118th_congress | 105 | 4,374 | 100.000% | 5,619 |

## Frozen Stage-A policy

- Primary actor universe: `all_serving_persons_during_118th_congress` (`105` persons).
- Reason: It preserves every valid nonempty-head event while retaining distinct persons throughout the completed Congress; no people are merged by Senate seat.
- The cap has deliberately **not** been selected in this audit. A separate cap-first audit reports retention, formal-concept feasibility, and candidate viability before any primary masking or model run.
