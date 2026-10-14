# R driver smoke test

Run the dependency-light specification test after R is available:

```bash
Rscript r/tests/test_model_drivers.R
```

It does **not** require `statnet`, `ergm`, `btergm`, `tergm`, or an input data file. It verifies the required static ladder labels `M0`–`M4c`, checks that degree/shared-partner/cyclic terms are present in the declared formulas, and numerically verifies the Proposition 6 lagged common-neighbor logistic ranking identity on the driver’s toy panel.

It also sources `score_masked_ergm.R` and verifies its default masked-scoring model selection, exact `conditional_predictions.csv` column contract, Statnet index-to-`nodes.csv$id` label mapping, tied-score ROC-AUC/PR-AUC behavior, degenerate-label status, leading-zero ID preservation, and the source-level conditional response call:

```r
predict(fit, conditional = TRUE, type = "response", output = "data.frame")
```

The test intentionally does **not** fit an ERGM or consume a pilot bundle. Once R and the project `renv` are available, run a small explicit mask export separately to exercise package/runtime behavior and inspect `model_status.csv` for every model/replicate result.

Full fitting is intentionally not tested against an implicit data file. Use an explicit, non-sensitive prepared CSV and inspect the driver manifests and status files described in [`r/models/README.md`](../models/README.md).

## Temporal btergm ladder source/base-R contract

```bash
Rscript r/tests/test_temporal_btergm_ladder.R
python -m pytest tests/test_temporal_btergm_driver.py
```

The dedicated temporal test needs **no modeling packages**. It verifies the exact
`T_tt/T0/T1/T2/T2_minus_H` definitions, fixed decays and CLI defaults, opaque
leading-zero labels, isolate preservation, exact consecutive integer/month
periods, strict input rejection, lagged OI/OO/II and degree matrix orientation,
future-panel independence, and btergm's temporal list-alignment contract. Its
source assertions prohibit prediction, simulation, and alternative estimation
engines. The Python source test runs without R; it additionally executes the
base-R test and validates a nonzero failure manifest when `Rscript` is available.

This is a contract test, not evidence of a fitted TERGM. Package-dependent fits
must be run separately on explicit bounded inputs. See
[`docs/TEMPORAL_BTERGM_LADDER.md`](../../docs/TEMPORAL_BTERGM_LADDER.md) for model
artifacts and the **MPLE conditional-score-only, never-forecast** interpretation.
