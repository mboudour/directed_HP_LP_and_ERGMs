# Network Science political-networks repositioning plan

**Decision date:** 25 October 2026
**Provisional venue:** *Network Science*, Special Collection, “Political Networks: New Trends & Directions”
**Submission deadline:** 13 November 2026

## Recommendation

I agree that the special collection is a strong and realistic target **if the Senate co-sponsorship analysis becomes the paper’s primary worked application, rather than a political example appended to an otherwise unchanged manuscript**. This is consistent with Philip Leifeld’s advice and with the call itself. The collection explicitly invites methodological innovation and empirical work on legislative processes, coalition formation, and representational relationships [1].

The existing benchmark should remain intact: it asks which object is missing and evaluates directed dyadic footprints, cap-first formal concepts, and recorded ordered group-event types separately. The Senate will supply the central substantive setting for that question. Enron and MathOverflow should remain in the paper as contrasting non-political cases that demonstrate that the benchmark is not tuned to one institution, but they should no longer lead the abstract, introduction, results narrative, or conclusion.

One important adjustment is needed to the premise that “framing can carry most of the political content.” Framing is necessary, but insufficient. The legislative application must generate the paper’s principal empirical questions and results:

1. When a recorded co-sponsorship group is partially withheld, do directed ERGM conditional scores improve recovery over transparent directed local statistics?
2. When the participant set is held fixed, can the score identify the bill sponsor, rather than merely exploiting group size or aggregate popularity?
3. Do groups derived from an aggregate co-sponsorship projection coincide with recorded bill coalitions, or do they mainly represent a different structural object?

The original missingness design remains a controlled stress test. It must **not** be described as evidence that the official legislative record is naturally MCAR or MNAR, nor as an estimate of actual archival incompleteness.

## A focused empirical design

### 1. Political event definition

Use a completed U.S. Senate Congress as the primary political core, provisionally the 118th Congress (2023–2024). It is recent, fully closed, and available in the official Bill Status archive. The archive covers the 108th through 119th Congresses, so the source choice is reproducible and does not depend on scraping [2].

For a Senate-originated measure, define one record as

\[
e_b=(\{s_b\},H_b),
\]

where $s_b$ is the bill sponsor and $H_b$ is the set of original co-sponsors. The official XML schema contains sponsor identifiers, each co-sponsor’s `isOriginalCosponsor` flag and `sponsorshipDate`, and the measure’s `introducedDate` [3]. This makes an “original co-sponsors at introduction” policy verifiable from a public source. Measures with no qualifying co-sponsor have an empty head and therefore lie outside the nonempty-head hyperarc target; report their number explicitly rather than silently discarding them.

Start with Senate bills (`S.`) as the main measure class. Audit joint resolutions, concurrent resolutions, and simple resolutions separately. They should enter the primary event set only if their sponsorship process and original-co-sponsor fields meet the same definition. Combining measure classes merely to increase sample size would blur the substantive event process.

### 2. Actor-universe policy before any model run

The Senate supplies 100 seats, but a two-year Congress can have more than 100 distinct people because of vacancies and replacements. Therefore, “one Congress equals a 100-person core” is a useful institutional motivation, not yet an actor definition.

The initial audit must compare at least two transparent policies:

- a fixed roster of 100 officeholders at a declared reference date, retaining events whose participants all belong to that roster; and
- the set of all unique serving persons, with its actual size reported.

Choose the primary universe only after the audit shows which policy preserves the event semantics and produces a coherent fixed network. Do not merge different people by Senate seat: that would manufacture continuity of actor identity. If a rigorously defined 100-person roster would exclude too much usable activity, retain the actual fixed person universe and describe it honestly. The benchmark does not require exactly 100 actors.

### 3. Cap gate: decide before full computation

The head cap is the central technical gate. Under the existing common cap $|T|,|H|\leq 3$, Senate events have $|T|=1$ but may have many original co-sponsors. The cap can therefore remove a substantively non-random subset of measures.

The first Senate audit should report, separately for records and distinct ordered types:

- the full distribution of original-head size;
- the share retained at caps 1, 2, 3, 5, and 10;
- static-footprint coverage at each cap;
- formal-concept counts, coverage, and enumeration time at the feasible caps; and
- the number of usable positives and structurally valid random, sponsor-substitution, and role-assignment candidates.

The default is to preserve cap three for the exact target-ladder comparison. A higher common Senate cap may become the primary Senate specification only if this audit shows that cap three is substantively unrepresentative **and** cap-first concept enumeration, candidate generation, and 30-mask computation all pass at the higher cap. If a higher cap is used, it must be declared before the full study, applied to all Senate target comparisons, and accompanied by a cap-three sensitivity. Do not enlarge the cap only for the native-event branch, because that would sever the direct event–concept fidelity comparison.

### 4. Political hard tests

The fixed-participant, fixed-arity role-assignment task is especially valuable in the Senate setting. It becomes the concrete question: among the legislators attached to a bill, which member is the sponsor and which members are original co-sponsors? This is an interpretable leadership and agenda-setting distinction.

Do **not** make the literal reversal $(T,H)\mapsto(H,T)$ the flagship political orientation test. For Senate events, that reversal changes a valid one-sponsor-to-many-co-sponsors grammar into an implausible many-sponsors-to-one-co-sponsor object. Retain it only as a clearly labelled structural stress test, if at all. The political hard negative should instead preserve the one-sponsor format: swap the recorded sponsor with one eligible co-sponsor, holding the participant set and arities fixed. This sponsor-substitution panel and the exhaustive role-assignment task are the appropriate primary tests of direction.

### 5. What remains unchanged

For the Senate core, retain the existing event-first type masks, MCAR and oracle activity-biased MNAR-out mechanisms, directed local scores, split-specific ERGM MPLE conditional scores, footprint summaries, random arity-matched panels, and within-network paired-mask inference. The score remains a conditional statistic, not a joint probability of a bill coalition. The bounded temporal branch remains outside Paper 1’s central claims.

The concept–event audit should be described prospectively and neutrally: it tests whether algebraically closed co-sponsorship groups equal recorded bill coalitions. It may reveal mismatch, as in the current cases, but the manuscript should state the observed result rather than assume that formal concepts are or are not political coalitions in advance.

## Implementation sequence and go/no-go gate

### Stage A — 25–28 October: source and event audit

1. Acquire one completed Congress from the official GPO Bill Status bulk archive. Use stable bill identifiers, `bioguideId` values, introduction dates, sponsor identifiers, original-co-sponsor flags, and co-sponsorship dates. Retain source URLs, checksums, schema version, and extraction logs. Congress.gov identifies its API as the preferred developer source and points to the same GPO bulk Bill Status data and user guide [3].
2. Build a new, data-specific provenance and audit pipeline. It must report measure classes, missing or duplicate identifiers, number of measures with zero original co-sponsors, original-head-size distributions, membership turnover, candidate roster policies, and all exclusions.
3. Freeze the event definition, measure-class rule, actor universe, and cap after reviewing these aggregate audits. Write them into the dataset registry and a Senate data-policy document before masking or model fitting.
4. Run a small end-to-end pilot: native-event build, binary directed projection, cap-first concept enumeration, one MCAR split, one activity-biased split, all candidate-panel constructors, and the complete ERGM score call.

**Go/no-go checkpoint:** proceed toward the special collection only when the source fields are complete enough for the event definition, the actor and cap policies are defensible, concept enumeration and candidate panels complete in practical time, and the pilot yields valid scores without changing the methods. If any of those conditions fails, preserve the existing paper’s evidence boundary and prepare it for the regular *Network Science* track without deadline pressure.

### Stage B — 29 October–4 November: preregistered-in-code Senate benchmark

5. Implement the frozen Senate configuration and add tests for event parsing, original-co-sponsor selection, actor policy, cap application, and sponsor-substitution candidates. Do not alter prior Enron or MathOverflow results.
6. Run the full Senate primary grid: 30 matched MCAR masks and 30 matched MNAR-out masks; random arity-matched ranking; sponsor-substitution and role-assignment evaluations; ERGM ladder conditional footprint scores; directed local-score references; and paired whole-mask bootstrap/sign-flip summaries.
7. Run only predeclared Senate supplements: cap-three sensitivity if the primary cap is larger, concept–event fidelity, and one clearly marked static directed-arc diagnostic. Do not introduce forecasting, STERGM, RHEM, neural baselines, House data, or cross-legislature panels during this submission window.
8. Publish only non-sensitive aggregate outputs, scripts, manifests, and checksums. The Senate source is public, but the existing Enron privacy boundary remains unchanged.

### Stage C — 5–9 November: political manuscript rebuild

9. Replace the current generic opening with a political problem statement: public records of legislative coalition formation may be represented as sponsor-to-original-co-sponsor events, but their dyadic projection does not preserve the event partition. Mention treaty signatories, joint statements, amicus coalitions, and diplomatic exchanges only as motivating examples; do not imply that they were analysed.
10. Make the Senate the first data section and first results section. Lead the abstract with the legislative event definition and the Senate result. Present Enron and MathOverflow afterwards as methodological scope checks with distinct record structures.
11. Rename results in political terms where warranted: sponsor identification, co-sponsorship coalition type, and projection-derived coalition. Keep the generic mathematical terms alongside them so that the benchmark remains portable.
12. Return to legislative interpretation in the discussion and conclusion. The claim should be limited to the specified Senate construction and controlled masks, while explaining why the design matters for political event data.
13. Use a provisional title without a colon:

   > **Exponential Random Graph Models as a Statistical Benchmark for Directed Link and Hyperlink Prediction in Legislative Co-sponsorship**

This keeps the planned methodological title while signalling that legislative co-sponsorship is central rather than incidental.

### Stage D — 10–13 November: blind submission package

14. Migrate the final manuscript to the *Network Science* LaTeX class/template and target the journal’s typical 20–40-page range. The current source architecture can remain, but the submission-facing source must use the Network Science template [4].
15. Create two distinct packages: an anonymised main manuscript and a title page. The journal requires authors, affiliations, acknowledgements where applicable, competing-interest, funding, and data-availability statements on the title page; the main document must be anonymised [4]. Remove author names and identifying headers from the blinded source. Cite the earlier EPJ Data Science article in the third person rather than as “our earlier work.”
16. Prepare a short cover-letter statement that selects **Political Networks: New Trends & Directions** in ScholarOne and explains the political question, Senate application, methodological innovation, and reproducibility materials.
17. Prepare 4–6 suggested reviewers with complementary expertise in political networks, legislative co-sponsorship, and ERGM methodology. Exclude collaborators, close personal contacts, institutional colleagues, recent coauthors, and the special-collection editors unless the submission system explicitly invites them.
18. Complete a final reproducibility, anonymisation, citation, figure, and statement audit on 12 November. Submit by 13 November rather than treating the date as a soft cutoff. The official call states that the deadline is 13 November 2026, specifies double-blind submission, and requires selection of the named special collection in the submission form [1].

## Scope guardrails

The time constraint makes the following boundaries essential:

- **One political primary application:** completed U.S. Senate co-sponsorship only. Do not add the House or other legislatures unless a compatible, audited pipeline already exists and does not delay the Senate analysis.
- **No change to the paper’s identity:** it remains a missingness-centred ERGM benchmark for directed link and hyperlink prediction.
- **No observational missing-data claim:** controlled omissions evaluate robustness; they do not diagnose the public legislative archive.
- **No full temporal-forecasting expansion:** TERGM, STERGM, RHEM, and rolling-origin forecasting remain the deferred Paper 2.
- **No result-driven cap or candidate policy:** every Senate design choice is frozen after Stage A and before the 30-mask runs.

## Immediate decision

Proceed with Stage A now. The first output is not a manuscript rewrite; it is a short audited Senate event-profile report that resolves the roster and cap questions. That audit is what determines whether the special-collection version is scientifically and operationally feasible before the firm deadline.

## References

[1]: https://www.cambridge.org/core/journals/network-science/announcements/call-for-papers/call-for-papers-political-networks-theory-methods-and-applications "Network Science Political Networks call for papers"

[2]: https://www.govinfo.gov/bulkdata/BILLSTATUS "GPO Bill Status bulk data repository"

[3]: https://www.congress.gov/help/using-data-offsite "Congress.gov guidance for developers using data offsite"

[4]: https://www.cambridge.org/core/journals/network-science/information/author-instructions/preparing-your-materials "Network Science preparing your materials"
