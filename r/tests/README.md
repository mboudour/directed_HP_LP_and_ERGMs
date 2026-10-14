# R driver smoke test

Run the dependency-light specification test after R is available:

```bash
Rscript r/tests/test_model_drivers.R
```

It does **not** require `statnet`, `ergm`, `btergm`, `tergm`, or an input data file. It verifies the required static ladder labels `M0`–`M4c`, checks that degree/shared-partner/cyclic terms are present in the declared formulas, and numerically verifies the Proposition 6 lagged common-neighbor logistic ranking identity on the driver’s toy panel.

Full fitting is intentionally not tested against an implicit data file. Use an explicit, non-sensitive prepared CSV and inspect the driver manifests and status files described in [`r/models/README.md`](../models/README.md).
