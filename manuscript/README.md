# Paper 1 manuscript workspace

The canonical submission-independent source is assembled in
`PAPER1_DRAFT.md`. Do not edit that generated file directly.

## Source order

1. `sections/00_title_abstract.md`
2. `sections/01_introduction.md`
3. `sections/02_target_ladder_and_score_logic.md`
4. `sections/03_data_and_methods.md`
5. `sections/05_results.md`
6. `sections/06_discussion.md`

`tables/` contains aggregate-only CSV and Markdown tables generated from the
published Phase 2 bundle. Its manifest records source checksums.

## Rebuild

```bash
make manuscript-tables
uv run python scripts/54_build_paper1_markdown.py
```

This workspace intentionally does not select a journal template or create a
Word/LaTeX submission file. Those formatting decisions remain separate from the
canonical Markdown evidence source.
