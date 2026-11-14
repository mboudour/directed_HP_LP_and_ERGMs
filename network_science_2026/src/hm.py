# ruff: noqa: E501
"""Higher-order ERGM: an ERGM of the two-mode incidence network of actors and hyperarcs.

Each observed record (a hyperarc with its multiplicity) is an event node; actor i is tied to
event b if i participates in b. Sufficient statistics (all genuine ERGM statistics of the
incidence network B):
  edges         number of actor-event ties
  activity      sum_i log(d_i!)             d_i: number of events of actor i
  size          sum_b log(|b|!)             |b|: number of participants of event b
  closure       sum_{i<k} log(s_ik!)        s_ik: number of events shared by i and k
  party, state  number of co-member pairs (within events) with the same party / state
  ideology      sum over co-member pairs of the absolute difference in ideology
The change statistic of the tie (i, b), with the rest of the network fixed, is
  1, log(1+d_i), log(1+|b\\i|), sum_{k in b\\i} log(1+s_ik), sum_{k in b\\i} 1[same party], ...
where d_i and s_ik exclude event b. HM0 omits closure. Parameters are estimated by maximum
pseudolikelihood (weighted logistic regression of all actor-event pairs, records weighted by
multiplicity). A candidate hyperarc with participants P is scored as a new event: the
geometric mean over i in P of the conditional probability of the tie (i, P), given the
training network and the other members of P. The model does not distinguish initiators.
"""

import numpy as np

TERMS_HM = ["edges", "activity", "size", "closure", "party", "state", "ideology"]
TERMS_HM0 = ["edges", "activity", "size", "party", "state", "ideology"]


def pair_mats(cov, n):
    same_p = (cov["party"][:, None] == cov["party"][None, :]).astype(float)
    same_s = (cov["state"][:, None] == cov["state"][None, :]).astype(float)
    dist = np.abs(cov["nominate"][:, None] - cov["nominate"][None, :])
    for M in (same_p, same_s, dist):
        np.fill_diagonal(M, 0)
    return {"party": same_p, "state": same_s, "ideology": dist}


def design(events, weights, n, cov):
    """Change statistics for all actor-event pairs of the training incidence network."""
    E = len(events)
    B = np.zeros((E, n))
    for e, P in enumerate(events):
        B[e, list(P)] = 1
    w = np.asarray(weights, float)
    deg = B.T @ w
    S = (B * w[:, None]).T @ B
    L0 = np.log1p(S)
    L1 = np.log1p(np.maximum(S - 1, 0))
    np.fill_diagonal(L0, 0)
    np.fill_diagonal(L1, 0)
    size = B.sum(1)
    X = {}
    X["edges"] = np.ones((E, n))
    X["activity"] = np.where(
        B > 0, np.log1p(np.maximum(deg[None, :] - 1, 0)), np.log1p(deg[None, :])
    )
    X["size"] = np.log1p(size[:, None] - B)
    X["closure"] = np.where(B > 0, B @ L1, B @ L0)
    for k, M in pair_mats(cov, n).items():
        X[k] = B @ M
    return B, X, deg, S


def fit(events, weights, n, cov, terms, ridge=1e-6, iters=50):
    B, X, deg, S = design(events, weights, n, cov)
    Xm = np.stack([X[t].ravel() for t in terms], 1)
    y = B.ravel()
    sw = np.repeat(np.asarray(weights, float), n)
    mu_, sd_ = Xm.mean(0), Xm.std(0)
    sd_[0] = 1.0
    mu_[0] = 0.0
    Z = (Xm - mu_) / sd_
    th = np.zeros(len(terms))
    for _ in range(iters):
        eta = Z @ th
        p = 1 / (1 + np.exp(-eta))
        g = Z.T @ (sw * (y - p)) - 2 * ridge * th
        H = (Z * (sw * p * (1 - p))[:, None]).T @ Z + 2 * ridge * np.eye(len(terms))
        step = np.linalg.solve(H, g)
        th += step
        if np.max(np.abs(step)) < 1e-8:
            break
    beta = th / sd_
    beta[0] = th[0] - (th[1:] * mu_[1:] / sd_[1:]).sum()
    return {"terms": terms, "theta": beta, "deg": deg, "S": S, "pair": pair_mats(cov, n)}


def score(model, P):
    """Geometric mean of conditional tie probabilities for a new event with participants P."""
    P = list(P)
    S, deg, pair = model["S"], model["deg"], model["pair"]
    lp = []
    for i in P:
        others = [k for k in P if k != i]
        x = {
            "edges": 1.0,
            "activity": np.log1p(deg[i]),
            "size": np.log1p(len(others)),
            "closure": float(np.log1p(S[i, others]).sum()),
        }
        for k, M in pair.items():
            x[k] = float(M[i, others].sum())
        eta = float(np.dot(model["theta"], [x[t] for t in model["terms"]]))
        lp.append(-np.logaddexp(0, -eta))
    return float(np.exp(np.mean(lp)))


# Standard statnet bipartite specification -------------------------------------------------
TERMS_STD = [
    "edges",
    "gwb1degree",
    "gwb2degree",
    "cycle4",
    "b1nodematch_party",
    "b1nodematch_state",
]


def design_std(events, weights, n, cov, tau, tau2=None):
    """Change statistics of the statnet terms edges, gwb1degree(tau), gwb2degree(tau), cycle(4),
    b1nodematch(party), b1nodematch(state) for all actor-event pairs (records as events)."""
    E = len(events)
    B = np.zeros((E, n))
    for e, P in enumerate(events):
        B[e, list(P)] = 1
    w = np.asarray(weights, float)
    r = 1 - np.exp(-tau)
    r2 = 1 - np.exp(-(tau if tau2 is None else tau2))
    deg = B.T @ w
    S = (B * w[:, None]).T @ B
    np.fill_diagonal(S, 0)
    size = B.sum(1)
    pm = pair_mats(cov, n)
    X = {
        "edges": np.ones((E, n)),
        "gwb1degree": r ** (deg[None, :] - B),
        "gwb2degree": r2 ** (size[:, None] - B),
        "cycle4": np.where(B > 0, B @ np.maximum(S - 1, 0), B @ S),
        "b1nodematch_party": B @ pm["party"],
        "b1nodematch_state": B @ pm["state"],
    }
    # for members, B @ (S - 1) includes the diagonal term max(S_ii - 1, 0) = 0 since diag(S) = 0
    return B, X, deg, S


def fit_std(
    events,
    weights,
    n,
    cov,
    taus=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0),
    taus2=(0.5, 1.0, 2.0),
    ridge=1e-6,
    iters=60,
):
    """Decays of gwb1degree (tau) and gwb2degree (tau2) selected jointly by profile pseudolikelihood."""
    best = None
    for tau, tau2 in [(a, b) for a in taus for b in taus2]:
        B, X, deg, S = design_std(events, weights, n, cov, tau, tau2)
        Xm = np.stack([X[t].ravel() for t in TERMS_STD], 1)
        y = B.ravel()
        sw = np.repeat(np.asarray(weights, float), n)
        mu_, sd_ = Xm.mean(0), Xm.std(0)
        mu_[0], sd_[0] = 0.0, 1.0
        sd_[sd_ == 0] = 1.0
        Z = (Xm - mu_) / sd_
        th = np.zeros(len(TERMS_STD))
        for _ in range(iters):
            eta = Z @ th
            p = 1 / (1 + np.exp(-eta))
            g = Z.T @ (sw * (y - p)) - 2 * ridge * th
            H = (Z * (sw * p * (1 - p))[:, None]).T @ Z + 2 * ridge * np.eye(len(th))
            step = np.linalg.solve(H, g)
            th += step
            if np.max(np.abs(step)) < 1e-8:
                break
        eta = Z @ th
        pl = float((sw * (y * eta - np.logaddexp(0, eta))).sum())
        beta = th / sd_
        beta[0] = th[0] - (th[1:] * mu_[1:] / sd_[1:]).sum()
        if best is None or pl > best["pl"]:
            best = {
                "terms": TERMS_STD,
                "theta": beta,
                "deg": deg,
                "S": S,
                "pair": pair_mats(cov, n),
                "tau": tau,
                "tau2": tau2,
                "pl": pl,
            }
    return best


def score_std(model, P):
    P = list(P)
    r = 1 - np.exp(-model["tau"])
    r2 = 1 - np.exp(-model["tau2"])
    S, deg, pair = model["S"], model["deg"], model["pair"]
    lp = []
    for i in P:
        others = [k for k in P if k != i]
        x = {
            "edges": 1.0,
            "gwb1degree": r ** deg[i],
            "gwb2degree": r2 ** len(others),
            "cycle4": float(S[i, others].sum()),
            "b1nodematch_party": float(pair["party"][i, others].sum()),
            "b1nodematch_state": float(pair["state"][i, others].sum()),
        }
        eta = float(np.dot(model["theta"], [x[t] for t in model["terms"]]))
        lp.append(-np.logaddexp(0, -eta))
    return float(np.exp(np.mean(lp)))
