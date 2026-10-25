# Auxiliary Mtt transitive-triple logistic fits

- Dataset: `senate_118_s_bills`
- Each split fits `y_ij ~ 1 + s_CN,ij` across every nonloop dyad in its observed projection.
- `s_CN` is the exact unweighted directed transitive-triple change statistic: OI + OO + II.
- This is the MPLE/logistic representation of an edges-plus-transitive-triple ERGM.
- The fit verifies the sign and induced arc-level ordering only; it is not a native-event score or a joint footprint probability.

## Completion

- Fits succeeded: 60/60

| Mechanism | Fits | Positive $\hat\theta_{tr}$ | Negative | Zero | Mean | SD | Range | Arc-level relation |
|---|---:|---:|---:|---:|---:|---:|---|---|
| mcar | 30 | 30 | 0 | 0 | 0.0571 | 0.0010 | [0.0542, 0.0593] | increasing_same_order_as_directed_CN |
| mnar_out | 30 | 30 | 0 | 0 | 0.0565 | 0.0009 | [0.0548, 0.0592] | increasing_same_order_as_directed_CN |
