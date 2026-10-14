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
