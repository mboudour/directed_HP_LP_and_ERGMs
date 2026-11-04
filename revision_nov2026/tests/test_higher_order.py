# ruff: noqa: E501
"""Change statistics of the undirected pairwise (um), higher-order (hm) and role-labelled
higher-order (hr) ERGMs agree with brute-force toggling of their sufficient statistics."""

import sys
from math import lgamma
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import hm  # noqa: E402
import hr  # noqa: E402
import um  # noqa: E402


def _cov(rng, n):
    return {
        "party": rng.integers(0, 3, n),
        "state": rng.integers(0, 4, n),
        "nominate": rng.normal(size=n),
    }


def test_hm_change_statistics():
    rng = np.random.default_rng(3)
    n, E = 9, 12
    cov = _cov(rng, n)
    B = (rng.random((E, n)) < 0.35).astype(float)
    for e in range(E):
        if B[e].sum() == 0:
            B[e, rng.integers(n)] = 1
    events = [set(np.nonzero(B[e])[0]) for e in range(E)]
    _, X, _, _ = hm.design(events, np.ones(E), n, cov)
    pm = hm.pair_mats(cov, n)
    iu = np.triu_indices(n, 1)

    def stats(B):
        S = B.T @ B
        g = {
            "edges": B.sum(),
            "activity": sum(lgamma(x + 1) for x in B.sum(0)),
            "size": sum(lgamma(x + 1) for x in B.sum(1)),
            "closure": sum(lgamma(x + 1) for x in S[iu]),
        }
        for k, M in pm.items():
            g[k] = float((M[iu] * S[iu]).sum())
        return g

    for e in range(E):
        for i in range(n):
            hi, lo = B.copy(), B.copy()
            hi[e, i], lo[e, i] = 1, 0
            a, b = stats(hi), stats(lo)
            for t in hm.TERMS_HM:
                assert np.isclose(a[t] - b[t], X[t][e, i]), (t, e, i)


def test_hr_change_statistics():
    rng = np.random.default_rng(5)
    n = 8
    recs = []
    for _ in range(25):
        P = rng.choice(n, rng.integers(2, 5), replace=False)
        recs.append((int(P[0]), frozenset(int(x) for x in P[1:])))

    def g(records):
        a, c, W = hr.counts(records, [1] * len(records), n)
        off = [(i, k) for i in range(n) for k in range(n) if i != k]
        return np.array(
            [
                sum(lgamma(x + 1) for x in a),
                sum(lgamma(x + 1) for x in c),
                sum(lgamma(W[i, k] + 1) for i, k in off),
                sum(W[i, k] * W[k, i] for i in range(n) for k in range(i + 1, n)),
            ]
        )

    a, c, W = hr.counts(recs, [1] * len(recs), n)
    for b, (s, H) in enumerate(recs):
        P = sorted({s, *H})
        rest = recs[:b] + recs[b + 1 :]
        base = g(rest)
        D = np.array([g([*rest, (v, frozenset(set(P) - {v}))]) - base for v in P])
        X = hr.features(a, c, W, P, exclude=(s, H))
        assert np.allclose(D - D[0], X - X[0]), b


def test_um_change_statistics():
    rng = np.random.default_rng(7)
    n = 10
    cov = _cov(rng, n)
    A = np.triu((rng.random((n, n)) < 0.4).astype(float), 1)
    A = A + A.T
    iu = np.triu_indices(n, 1)
    for tau in (0.5, 2.0, 4.0):
        r = 1 - np.exp(-tau)

        def f(k, tau=tau, r=r):
            return np.exp(tau) * (1 - r**k)

        def stats(A, f=f):
            SP = A @ A
            return np.array([A[iu].sum(), f(A.sum(1)).sum(), (A[iu] * f(SP[iu])).sum()])

        X = um.change_stats(A, cov, tau)
        for i, j in zip(*iu, strict=True):
            hi, lo = A.copy(), A.copy()
            hi[i, j] = hi[j, i] = 1
            lo[i, j] = lo[j, i] = 0
            d = stats(hi) - stats(lo)
            assert np.allclose(d, [X["edges"][i, j], X["gwdegree"][i, j], X["gwesp"][i, j]]), (
                tau,
                i,
                j,
            )
