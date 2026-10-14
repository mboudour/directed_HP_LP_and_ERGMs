# MathOverflow reconstruction-profile protocol

`make phase2-mathoverflow-profile` produces a descriptive, non-sensitive profile
from `Posts.xml`. It does **not** create native events or approve a
reconstruction policy.

The profile treats an event candidate as a question with one or more distinct,
non-self answerers. It reports first-answerer timing and group-size evidence for
five descriptive response windows: 1, 7, 30, 90, and 365 calendar days. It also
reports ownerless questions and answers, answers whose parent is not an eligible
question, self-answers, and duplicate eligible answer records.

## Profile-based recommendation — pending approval

Use a **30-day** primary window, with **7- and 90-day** sensitivity windows.
The observed profile retains 85.092% of distinct eligible question-answerer
pairs and 96.172% of questions with an answerer by 30 days. The long response
tail is material: the 90th percentile is 216.407 days and the 95th percentile
is 985.838 days. A 365-day profile remains descriptive rather than an analytic
sensitivity because it can pool much later, potentially distinct, answer cycles
into the same reconstructed group.

The recommended policy retains only public-dump rows, excludes comments and
anonymous users, excludes self-answers, and collapses repeated answers by the
same user to the same question. It is recorded but not approved in
`data/metadata/gates/mathoverflow_reconstruction_policy.json`.

This evidence is used to choose one declared reconstruction rule later. If that
rule is approved, `scripts/24_prepare_mathoverflow.py` will construct exactly:

`{distinct answerers within the fixed window} → {question asker}`

The approved policy must keep comments excluded, exclude anonymous users,
collapse duplicate answerers per question, and retain only rows present in the
public dump. A reconstructed group is an analyst-defined answer-window object,
not an observed multi-recipient communication event.

Run:

```bash
make phase2-mathoverflow-profile
```

The tracked code and documentation are versioned. Source XML, audit JSON, and
profile outputs remain local under the project's data and results directories.
