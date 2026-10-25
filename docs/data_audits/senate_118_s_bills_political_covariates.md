# 118th Senate political covariate preparation

## Fixed actor policy

The static benchmark uses the complete 118th-Senate actor universe from the audited bill-event construction. Party is affiliation at the beginning of the actor's 118th service (2023-01-03 for incumbents), state is the serving state, and ideology is Voteview's first-dimension DW-NOMINATE estimate. This is a static covariate policy; it does not treat party or ideology as a time-varying event covariate.
Majority-caucus entry is coded one for Democratic and Independent actors and zero for Republican actors, reflecting the 118th Senate's Democratic/Independent majority caucus. Senate seniority is cumulative completed Senate service before the actor's own 118th-service entry date, expressed in years.

## Join checks

- Senate actors: `105`
- Roster matches: `105`
- Voteview matches: `105`
- States represented: `50`
- Party-at-entry categories: `{'Democrat': 52, 'Independent': 3, 'Republican': 50}`
- Majority-caucus entrants: `55`
- Senate seniority years at service entry (median): `10.00`
- Actors with a recorded affiliation change during the Congress: `1`
- 2 exceptional Voteview join(s) used a documented key rule; no score-value-based selection was used.

The generated node-level table remains excluded from version control. The tracked metadata file records only aggregate counts, source paths, and checksums.
