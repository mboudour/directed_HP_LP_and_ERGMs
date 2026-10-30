# Paper 2 temporal RHEM working draft

This directory contains a **working manuscript for methodological discussion**, not a submission-ready paper.

- `Paper2_TemporalRHEM.tex` — primary LaTeX source.
- `Paper2_TemporalRHEM.bib` — compact bibliography with verified RHEM, event-model, TERGM, btergm, Eventnet, and Enron sources.
- `tables/` — generated TeX tables from aggregate-only output.
- `figures/` — generated sensitivity figure.
- `Paper2_TemporalRHEM.pdf` — locally compiled review copy.

## Manuscript build

From this directory, run the ordinary sequence:

```bash
pdflatex Paper2_TemporalRHEM.tex
bibtex Paper2_TemporalRHEM
pdflatex Paper2_TemporalRHEM.tex
pdflatex Paper2_TemporalRHEM.tex
```

No journal class is required. The document uses the standard `article` class.

## Rebuilding numerical material

From the repository root, after private Eventnet input and fit bundles have been generated:

```bash
uv run python scripts/79_summarize_enron_rhem_sensitivities.py \
  --primary results/models/enron_temporal_rhem_rolling_seed20261030_ascending \
  --sampling-sensitivity results/models/enron_temporal_rhem_rolling_seed20261031_ascending \
  --tie-sensitivity results/models/enron_temporal_rhem_rolling_seed20261030_descending \
  --footprint-collapse-sensitivity results/models/enron_temporal_rhem_rolling_seed20261030_ascending_collapsed \
  --output-dir results/published/paper2_temporal_20261030 --overwrite
uv run python scripts/80_build_paper2_materials.py
```

The table/figure builder reads only `results/published/paper2_temporal_20261030/` and the aggregate temporal readiness audit. It does not read private actor IDs, native-event rows, candidate sets, or Eventnet covariate rows.

## Interpretation boundary

The completed RHEM evidence is a conditional receiver-set ranking exercise: given the observed sender and receiver-set size, it ranks the observed set against Eventnet-sampled same-size alternatives. It is neither an unconditional email-event probability nor a model for sender selection, timing, or receiver-set size.

The primary source-record representation has 108 multiple-receiver test events. The same-timestamp identical-footprint collapse sensitivity has 48. The group-history contrast changes sign on conditional log score under that representation change. The manuscript deliberately reports this as a feasibility finding, not as a stable higher-order result.

Before any submission, the study still requires a batch-history tie sensitivity, further fixed-seed risk-set repetitions, and a longer pre-specified dyadic temporal-ERGM panel.
