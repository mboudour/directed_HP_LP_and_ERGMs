# MathOverflow Stack Exchange public-data snapshot — April 2024

## Source and local acquisition

- Dataset: MathOverflow public Stack Exchange data dump.
- Current official data-dump access page:
  https://mathoverflow.net/help/data-dumps
- Archived source snapshot:
  https://archive.org/download/stackexchange/mathoverflow.net.7z
- Archive snapshot date: 2024-04-07.
- Retrieved: 2026-10-13.
- Archive location:
  `data/external/mathoverflow_stackexchange_2024/mathoverflow.net.7z`
- Archive SHA-256:
  `4728b0e0aa501eb5c35b03eddf8e0059249a74181506abd1ff7d573fa46b016b`

## Preserved raw records

- Extracted `Posts.xml`:
  `data/raw/mathoverflow_stackexchange_2024/Posts.xml`
- Extracted `Users.xml`:
  `data/raw/mathoverflow_stackexchange_2024/Users.xml`
- `Comments.xml` and `PostHistory.xml` remain inside the source archive and are intentionally not extracted.

## Proposed event reconstruction

A question is identified by a `Posts.xml` row with `PostTypeId = 1`.
An answer is identified by a row with `PostTypeId = 2` whose `ParentId` is the question identifier.

For a declared answer window, construct one directed native event:

`{distinct answerer user IDs} → {question asker user ID}`

The construction is an analyst-defined reconstruction from question and answer records. It is not a directly recorded multi-recipient message event.

## Supported targets

- Directed arc recovery: yes.
- Directed footprint completion: yes.
- Formal-concept recovery: yes, after directed graph aggregation.
- Native-event recovery: conditional, after a reproducible answer-window rule is fixed.
- Conditional role assignment: yes, under the reconstructed answerer-to-asker roles.

## Processing constraints

- Preserve the `.7z` archive and extracted XML files unchanged.
- Exclude comments from the primary construction.
- Record the question-answer time window, deleted-post treatment, anonymous-user treatment, and duplicate-answerer rule before generating derived data.
- Do not commit the archive or extracted XML files to Git.
