# ruff: noqa: E501
"""Undirected pairwise ERGM: an ERGM of the clique graph (undirected 2-section) of the records.

Two actors are adjacent if they participate together in at least one training record.
Terms: edges; geometrically weighted degree G = sum_i f(d_i); geometrically weighted
edgewise shared partners W = sum_{edges ij} f(sp_ij); party and state matching; absolute
difference in ideology. f(k) = e^tau [1 - (1 - e^-tau)^k]. Estimation by MPLE; the decay is
selected by profile pseudolikelihood over a grid. A candidate hyperedge P is scored by the
geometric mean of the conditional edge probabilities over all pairs of P.
"""

import numpy as np

TERMS = ["edges", "gwdegree", "gwesp", "party", "state", "ideology"]
TAU_GRID = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]


def clique_graph(events, n):
    A = np.zeros((n, n))
    for P in events:
        P = list(P)
        A[np.ix_(P, P)] = 1
    np.fill_diagonal(A, 0)
    return A


def change_stats(A, cov, tau):
    r = 1 - np.exp(-tau)
    d = A.sum(1)
    D0 = d[:, None] - A  # degree of i without the dyad (i, j)
    gwdeg = r**D0 + r**D0.T
    SP = A @ A
    np.fill_diagonal(SP, 0)
    f = np.exp(tau) * (1 - r**SP)
    R1 = r**SP
    R2 = r ** np.maximum(SP - 1, 0)
    T1 = (A * R1) @ A
    T2 = (A * R2) @ A
    gwesp = f + np.where(A > 0, T2 + T2.T, T1 + T1.T)
    X = {
        "edges": np.ones_like(A),
        "gwdegree": gwdeg,
        "gwesp": gwesp,
        "party": (cov["party"][:, None] == cov["party"][None, :]).astype(float),
        "state": (cov["state"][:, None] == cov["state"][None, :]).astype(float),
        "ideology": np.abs(cov["nominate"][:, None] - cov["nominate"][None, :]),
    }
    if "logcount" in cov:
        X["logcount"] = np.asarray(cov["logcount"], float)
    return X


def _logit(Xm, y, ridge=1e-6, iters=60):
    mu, sd = Xm.mean(0), Xm.std(0)
    mu[0], sd[0] = 0.0, 1.0
    sd[sd == 0] = 1.0
    Z = (Xm - mu) / sd
    th = np.zeros(Z.shape[1])
    for _ in range(iters):
        eta = Z @ th
        p = 1 / (1 + np.exp(-eta))
        g = Z.T @ (y - p) - 2 * ridge * th
        H = (Z * (p * (1 - p))[:, None]).T @ Z + 2 * ridge * np.eye(len(th))
        step = np.linalg.solve(H, g)
        th += step
        if np.max(np.abs(step)) < 1e-8:
            break
    eta = Z @ th
    pl = float((y * eta - np.logaddexp(0, eta)).sum())
    beta = th / sd
    beta[0] = th[0] - (th[1:] * mu[1:] / sd[1:]).sum()
    return beta, pl


def fit(events, n, cov, taus=TAU_GRID, terms=None):
    terms = TERMS if terms is None else terms
    A = clique_graph(events, n)
    iu = np.triu_indices(n, 1)
    y = A[iu]
    best = None
    prof = {}
    for tau in taus:
        X = change_stats(A, cov, tau)
        Xm = np.stack([X[t][iu] for t in terms], 1)
        beta, pl = _logit(Xm, y)
        prof[tau] = pl
        if best is None or pl > best[2]:
            best = (tau, beta, pl, X)
    tau, beta, _, X = best
    eta = sum(beta[k] * X[t] for k, t in enumerate(terms))
    P = 1 / (1 + np.exp(-eta))
    return {"tau": tau, "theta": beta, "P": P, "profile": prof, "terms": terms}


def score(model, P):
    P = sorted(P)
    iu = np.triu_indices(len(P), 1)
    p = np.clip(model["P"][np.ix_(P, P)][iu], 1e-300, 1)
    return float(np.exp(np.log(p).mean()))
