"""Bipartite change statistics of run_fec agree with brute-force toggling."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import run_fec  # noqa: E402


def _f(k, tau):
    return np.exp(tau) * (1 - (1 - np.exp(-tau)) ** k)


def _stats(Y, tau):
    A = Y.astype(float)
    S = A @ A.T
    T = A.T @ A
    iu = np.triu_indices(A.shape[0], 1)
    ju = np.triu_indices(A.shape[1], 1)
    return np.array(
        [
            _f(A.sum(1), tau).sum(),
            _f(A.sum(0), tau).sum(),
            _f(S[iu], tau).sum(),
            _f(T[ju], tau).sum(),
        ]
    )


def test_bipartite_change_stats():
    rng = np.random.default_rng(1)
    for tau in (0.5, 2.0, 4.0):
        Y = (rng.random((7, 9)) < 0.4).astype(np.int8)
        cs = run_fec.bipartite_change_stats(Y, tau)
        for i in range(Y.shape[0]):
            for j in range(Y.shape[1]):
                hi, lo = Y.copy(), Y.copy()
                hi[i, j], lo[i, j] = 1, 0
                d = _stats(hi, tau) - _stats(lo, tau)
                got = [cs[k][i, j] for k in ("gwb1degree", "gwb2degree", "gwb1dsp", "gwb2dsp")]
                assert np.allclose(d, got), (tau, i, j, d, got)
