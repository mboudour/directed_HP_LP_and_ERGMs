# MathOverflow reconstruction-profile protocol

`make phase2-mathoverflow-profile` produces a descriptive, non-sensitive profile
from `Posts.xml`. It does **not** create native events or approve a
reconstruction policy.

The profile treats an event candidate as a question with one or more distinct,
non-self answerers. It reports first-answerer timing and group-size evidence for
five descriptive response windows: 1, 7, 30, 90, and 365 calendar days. It also
reports ownerless questions and answers, answers whose parent is not an eligible
question, self-answers, and duplicate eligible answer records.

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
