# ruff: noqa: E501
"""Bootstrapped MPLE for a TERGM with lagged and exogenous edge covariates only, as in btergm.

With no within-period dependence terms, the MPLE is the logistic regression of the arcs of all
periods on the edge covariates (pooled over periods), and btergm's confidence intervals
resample periods with replacement. This module computes the same estimator with float32
design blocks, for networks too large for btergm in the available memory.
"""

import numpy as np


def _fit(blocks, w=None, iters=50, th0=None):
    p = blocks[0][0].shape[1]
    th = np.zeros(p) if th0 is None else th0.copy()
    w = np.ones(len(blocks)) if w is None else w
    for _ in range(iters):
        g = np.zeros(p)
        H = np.zeros((p, p))
        for (X, y), wt in zip(blocks, w, strict=True):
            if wt == 0:
                continue
            eta = X @ th.astype(np.float32)
            mu = 1 / (1 + np.exp(-eta.astype(np.float64)))
            g += wt * (X.T @ (y - mu))
            H += wt * ((X * (mu * (1 - mu))[:, None].astype(np.float32)).T @ X).astype(np.float64)
        step = np.linalg.solve(H + 1e-9 * np.eye(p), g)
        th += step
        if np.max(np.abs(step)) < 1e-7:
            break
    return th


def fit(blocks, R=100, seed=20261104):
    """blocks: list over periods of (X float32 [rows x p], y float64). Returns estimate and 95% interval."""
    est = _fit(blocks)
    rng = np.random.default_rng(seed)
    T = len(blocks)
    reps = []
    for _ in range(R):
        w = np.bincount(rng.integers(0, T, T), minlength=T).astype(float)
        reps.append(_fit(blocks, w=w, th0=est, iters=30))
    reps = np.array(reps)
    return est, np.percentile(reps, 2.5, axis=0), np.percentile(reps, 97.5, axis=0)
