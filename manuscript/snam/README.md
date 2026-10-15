# Paper 1 SNAM TeX source package

This directory is the **journal-portable TeX source** for Paper 1, prepared with _Social Network Analysis and Mining_ (SNAM) as the tentative target. It deliberately uses the standard `article` class rather than a journal-specific class so that a future retargeting decision does not require rebuilding the scientific manuscript.

## Source package

- `Paper1_SNAM.tex` — complete manuscript source, including eight main evidence tables.
- `Paper1_SNAM.bib` — 18 verified, cited bibliography records in author--year style.
- `figures/` — three aggregate-only vector figures, with PNG review copies:
  - `Fig1_target_ladder.pdf`
  - `Fig2_concept_event_fidelity.pdf`
  - `Fig3_primary_panel_profiles.pdf`

All table values and figures are based on tracked aggregate-safe outputs. The package excludes raw source data, email contents, address maps, actor identifiers, candidate-level predictions, and generated build intermediates.

## Compile locally

Compile from this directory with a standard `pdflatex` and BibTeX installation:

```bash
pdflatex Paper1_SNAM.tex
bibtex Paper1_SNAM
pdflatex Paper1_SNAM.tex
pdflatex Paper1_SNAM.tex
pdflatex Paper1_SNAM.tex
```

The final three TeX runs resolve author--year citations, cross-references, tables, and figures. The source was independently validated with this sequence using standard TeX packages and produced a 24-page draft. Its heuristic main-prose count, excluding display environments, is 9,482 words, within the project’s 8,000--9,500-word SNAM calibration range.

## Required author completion

The manuscript identifies Moses Boudourides, the School of Professional Studies at Northwestern University, and the supplied correspondence email. It intentionally leaves bracketed author-confirmation text for funding, competing interests, ethics/consent, final data/code-access wording, and any applicable generative-AI disclosure. These statements must be completed and approved by the authors before submission.

## Rebuilding figures

The figure source is `scripts/56_build_snam_figures.py`. It uses only aggregate CSV tables under `manuscript/tables/` and writes the figure pair formats to `figures/`. The plan-aligned static/concept tables are built by `scripts/58_build_plan_aligned_tables.py`, and the aggregate-only orientation table by `scripts/57_extract_orientation_accuracy.py`. Run `make manuscript-snam` from the project root to regenerate required tables and figures before compiling.
