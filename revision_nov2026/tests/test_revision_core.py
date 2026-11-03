"""Unit tests for the revision re-implementation (synthetic toy graphs only)."""

import itertools
import sys
from math import comb
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import benchmark  # noqa: E402
import ergm  # noqa: E402
import events  # noqa: E402


def _toy(n=9, p=0.35, seed=1):
    rng = np.random.default_rng(seed)
    Y = (rng.random((n, n)) < p).astype(np.int8)
    np.fill_diagonal(Y, 0)
    cov = {
        "party": rng.integers(0, 3, n),
        "caucus": rng.integers(0, 2, n),
        "state": rng.integers(0, 3, n),
        "nominate": rng.normal(size=n),
        "majority": rng.integers(0, 2, n).astype(float),
        "seniority": rng.integers(0, 20, n).astype(float),
    }
    return Y, cov


def test_change_statistics_match_bruteforce_toggles():
    Y, cov = _toy()
    terms = ergm.LADDER["M6"] + ["ttriple"]
    cs = ergm.change_stats(Y, terms, cov)
    n = Y.shape[0]
    for i, j in itertools.permutations(range(n), 2):
        yp, ym = Y.copy(), Y.copy()
        yp[i, j], ym[i, j] = 1, 0
        d = ergm.stat_vector(yp, terms, cov) - ergm.stat_vector(ym, terms, cov)
        assert np.allclose(d, [cs[t][i, j] for t in terms])


def test_ttriple_change_is_total_common_neighbours():
    Y, cov = _toy(seed=2)
    A = Y.astype(float)
    oo, ii = A @ A.T, A.T @ A
    np.fill_diagonal(oo, 0)
    np.fill_diagonal(ii, 0)
    cs = ergm.change_stats(Y, ["ttriple"])["ttriple"]
    off = ~np.eye(Y.shape[0], dtype=bool)
    assert np.allclose(cs[off], (A @ A + oo + ii)[off])


def test_single_dyad_change_matches_vectorised():
    Y, cov = _toy(n=10, seed=3)
    terms = ergm.LADDER["M6"]
    cs = ergm.change_stats(Y, terms, cov)
    for i, j in itertools.permutations(range(10), 2):
        assert np.allclose(
            benchmark._single_change(Y, i, j, terms, cov), [cs[t][i, j] for t in terms]
        )


def test_joint_footprint_probability_by_enumeration():
    Y, cov = _toy(n=10, seed=4)
    terms = ergm.LADDER["M5"]
    theta = np.random.default_rng(5).normal(size=len(terms)) * 0.3
    s, H = 0, [2, 5, 7]
    lp = benchmark.joint_footprint_logprob(Y, s, H, terms, theta, cov)
    y0 = Y.copy()
    y0[s, H] = 0
    w = []
    for z in itertools.product([0, 1], repeat=len(H)):
        yz = y0.copy()
        yz[s, H] = z
        w.append(theta @ ergm.stat_vector(yz, terms, cov))
    assert np.isclose(lp, w[-1] - np.logaddexp.reduce(w))


def test_kappa_counts_covers_of_a_set():
    def kappa(n):
        return sum((-1) ** k * comb(n, k) * 2 ** (2 ** (n - k) - 1) for k in range(n + 1))

    def brute(n):
        subsets = [
            frozenset(c) for r in range(1, n + 1) for c in itertools.combinations(range(n), r)
        ]
        count = 0
        for m in range(2 ** len(subsets)):
            fam = [subsets[b] for b in range(len(subsets)) if m >> b & 1]
            if frozenset().union(*fam) == frozenset(range(n)):
                count += 1
        return count

    assert [kappa(n) for n in range(4)] == [brute(n) for n in range(4)] == [1, 1, 5, 109]


def test_concepts_are_closed_pairs():
    Y, _ = _toy(n=8, p=0.5, seed=6)
    for T, H in events.concepts(Y, 3, 8):
        up = frozenset.intersection(*[frozenset(np.nonzero(Y[i])[0]) for i in T])
        down = frozenset.intersection(*[frozenset(np.nonzero(Y[:, j])[0]) for j in H])
        assert up == H and down == T


def test_role_metrics_tie_handling():
    assert benchmark.role_metrics([1.0, 1.0, 0.0], 0) == (0.5, 0.75)
    assert benchmark.role_metrics([0.0, 1.0, 2.0], 0) == (0.0, 1 / 3)


def test_sender_receiver_sparse_matches_dense():
    Y, cov = _toy(n=30, p=0.3, seed=7)
    terms = ergm.LADDER["S1"]
    X, y, _ = ergm.design(Y, terms, cov, sparse=False)
    b1, _ = ergm.mple(X, y)
    Xs, ys, _ = ergm.design(Y, terms, cov, sparse=True)
    b2, _ = ergm.mple(Xs, ys)
    p1, _ = ergm.conditional_probs(Y, terms, b1, cov)
    p2, _ = ergm.conditional_probs(Y, terms, b2, cov)
    off = ~np.eye(30, dtype=bool)
    assert np.abs(p1[off] - p2[off]).max() < 1e-5
