# Enron temporal directed-hyperevent readiness audit

## Scope

This audit describes the existing Enron custodian native-event projection as an
input for a separate temporal directed-group-event study. It does not alter the
Paper 1 static projection, deduplicate source records, fit an RHEM, or make a
forecasting claim.

The event unit is one recorded email with one sender and a nonempty unordered
set of To-plus-Cc recipients. The actor policy and source date filter are the
already documented custodian projection policy.

- Event records: `5,231`
- Actors: `50`
- Sender actors: `48`
- UTC span: `1999-05-11T09:27:00+00:00` to `2001-12-31T15:55:59+00:00`
- Months with one or more events: `32`
- Events with two or more recipients: `178`

## Origin-safe actor universe and forecast folds

The primary temporal pilot freezes `50`
actors by total sender-or-receiver participation strictly before
`2001-01-01T00:00:00+00:00`. Lexical actor identity
is only a deterministic tie-break. An event is retained only when its sender
and every receiver belong to this pre-origin universe. The retained sequence
contains `2,434`
pre-origin events and `5,231`
events before the exclusive evaluation endpoint
`2002-01-01T00:00:00+00:00`. This prevents
the actor-selection rule from ranking the evaluation universe with future
participation.

The private bundle contains four predeclared expanding 2001 quarterly folds.
Each test event may use the history of earlier observed events, but model
coefficients must be estimated only from records preceding that fold's origin.

## Receiver-set sizes

| Recipients | Events |
|---:|---:|
| 1 | 5,053 |
| 2 | 169 |
| 3 | 5 |
| 4 | 4 |

## Simultaneous-event sensitivity

The archive retains distinct source records under the existing message-copy
policy. `4,699` records occur in timestamp
ties across `1,803` distinct timestamps; the
largest tie contains `8` records.
`4,699` records occur in
groups sharing a timestamp, sender, and target set. These quantities do not
establish that such records are copies or duplicates; they show why a temporal
history model must expose its treatment of tied event times.

The Eventnet preparation records a deterministic interval order
`event_id_ascending`. That order is not given a substantive
interpretation. The companion descending/ascending bundle is a required
sensitivity analysis before interpreting history-dependent effects.

## Candidate-event contract

The generated Eventnet configuration uses `COND_SIZE_DHE_OBS` with
`100` sampled controls per
observed event. It conditions on recipient-set size. One observation is a full
sender-plus-recipient-set choice; the second additionally conditions on the
observed sender. The RHEM literature motivates sampled risk sets because the
full set of receiver subsets is exponential in the number of actors.

The history covariates have a `604,800`
second decay half-life. They include whole-event repetition, directed dyad
repetition, directed reciprocation, receiver-pair repetition, receiver
interaction, and directed transitive closure. A later fitted analysis must
report the Eventnet version, random-sampling behavior, selected observation,
rolling-origin training boundary, and tied-time sensitivity.

## Monthly distribution

| Month | Events |
|:---|---:|
| 1999-05 | 21 |
| 1999-06 | 10 |
| 1999-07 | 22 |
| 1999-08 | 40 |
| 1999-09 | 64 |
| 1999-10 | 44 |
| 1999-11 | 16 |
| 1999-12 | 52 |
| 2000-01 | 55 |
| 2000-02 | 60 |
| 2000-03 | 57 |
| 2000-04 | 162 |
| 2000-05 | 193 |
| 2000-06 | 219 |
| 2000-07 | 164 |
| 2000-08 | 225 |
| 2000-09 | 231 |
| 2000-10 | 180 |
| 2000-11 | 341 |
| 2000-12 | 278 |
| 2001-01 | 287 |
| 2001-02 | 327 |
| 2001-03 | 400 |
| 2001-04 | 327 |
| 2001-05 | 415 |
| 2001-06 | 141 |
| 2001-07 | 104 |
| 2001-08 | 52 |
| 2001-09 | 113 |
| 2001-10 | 339 |
| 2001-11 | 218 |
| 2001-12 | 74 |

## Boundary

This is a data and risk-set readiness record. It is not a fitted RHEM,
TERGM, STERGM, or out-of-sample forecast result.
