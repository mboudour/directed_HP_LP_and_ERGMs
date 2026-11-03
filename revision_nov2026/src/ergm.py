"""Directed ERGM change statistics, MPLE and conditional tie probabilities.

Terms follow the statnet `ergm` definitions with fixed decays:
edges, mutual, gwodegree(a), gwidegree(a), dgwesp(b, OTP/OSP/ISP), ctriple,
nodematch, absdiff, nodeocov. All change statistics are computed for every
ordered dyad (i, j), i != j, as g(Y with ij) - g(Y without ij).
"""

import numpy as np
from scipy.optimize import minimize

DECAY = 0.5


def _gw_inc(c, decay):
    """f(c+1) - f(c) for f(c) = e^d [1 - (1 - e^-d)^c]."""
    return (1.0 - np.exp(-decay)) ** c


def _gw_f(c, decay):
    return np.exp(decay) * (1.0 - (1.0 - np.exp(-decay)) ** c)


def change_stats(Y, terms, cov=None, decay=DECAY):
    """Return dict term -> (n x n) array of change statistics."""
    A = Y.astype(np.float64)
    n = A.shape[0]
    out = {}
    Yb = Y.astype(bool)
    dout = A.sum(1)
    din = A.sum(0)
    if "edges" in terms:
        out["edges"] = np.ones((n, n))
    if "mutual" in terms:
        out["mutual"] = A.T.copy()
    if "gwodegree" in terms:
        # out-degree of i excluding arc ij
        d = dout[:, None] - A
        out["gwodegree"] = _gw_inc(d, decay)
    if "gwidegree" in terms:
        d = din[None, :] - A
        out["gwidegree"] = _gw_inc(d, decay)
    if any(t.startswith("dgwesp") for t in terms):
        OI = A @ A  # i->k->j
        OO = A @ A.T  # i->k, j->k
        II = A.T @ A  # k->i, k->j
        np.fill_diagonal(OO, 0)
        np.fill_diagonal(II, 0)
        r = 1.0 - np.exp(-decay)

        def W(C, shift):
            return np.where(C - shift >= 0, r ** np.clip(C - shift, 0, None), 0.0)

        sel = Yb  # whether arc ij is present (then partner counts include it)
        if "dgwesp_OTP" in terms:
            own = _gw_f(OI, decay)
            W0, W1 = A * W(OI, 0), A * W(OI, 1)
            t1 = np.where(sel, W1 @ A.T, W0 @ A.T)  # arcs i->l with j->l
            t2 = np.where(sel, A.T @ W1, A.T @ W0)  # arcs l->j with l->i
            out["dgwesp_OTP"] = own + t1 + t2
        if "dgwesp_OSP" in terms:
            own = _gw_f(OO, decay)
            W0, W1 = A * W(OO, 0), A * W(OO, 1)
            ta = np.where(sel, W1 @ A, W0 @ A)  # arcs i->l, l->j
            tb = np.where(sel, W1.T @ A, W0.T @ A)  # arcs l->i, l->j
            out["dgwesp_OSP"] = own + ta + tb
        if "dgwesp_ISP" in terms:
            own = _gw_f(II, decay)
            W0, W1 = A * W(II, 0), A * W(II, 1)
            ta = np.where(sel, A @ W1.T, A @ W0.T)  # arcs j->l, i->l
            tb = np.where(sel, A @ W1, A @ W0)  # arcs l->j, i->l
            out["dgwesp_ISP"] = own + ta + tb
    if "ctriple" in terms:
        out["ctriple"] = (A @ A).T  # j->k->i
    if "ttriple" in terms:
        OI = A @ A
        OO = A @ A.T
        II = A.T @ A
        np.fill_diagonal(OO, 0)
        np.fill_diagonal(II, 0)
        out["ttriple"] = OI + OO + II
    if cov is not None:
        if "nodematch_party" in terms:
            p = cov["party"]
            out["nodematch_party"] = (p[:, None] == p[None, :]).astype(float)
        if "nodematch_state" in terms:
            s = cov["state"]
            out["nodematch_state"] = (s[:, None] == s[None, :]).astype(float)
        if "absdiff_nominate" in terms:
            z = cov["nominate"]
            out["absdiff_nominate"] = np.abs(z[:, None] - z[None, :])
        if "nodeocov_majority" in terms:
            out["nodeocov_majority"] = np.repeat(cov["majority"][:, None], n, 1).astype(float)
        if "nodeocov_seniority" in terms:
            out["nodeocov_seniority"] = np.repeat(cov["seniority"][:, None], n, 1).astype(float)
    return {t: out[t] for t in terms}


LADDER = {
    "M0": ["edges"],
    "M1": ["edges", "mutual"],
    "M2": ["edges", "mutual", "gwodegree", "gwidegree"],
    "M3": ["edges", "mutual", "gwodegree", "gwidegree", "dgwesp_OTP"],
    "M4": ["edges", "mutual", "gwodegree", "gwidegree", "dgwesp_OTP", "dgwesp_OSP", "dgwesp_ISP"],
    "M4c": [
        "edges",
        "mutual",
        "gwodegree",
        "gwidegree",
        "dgwesp_OTP",
        "dgwesp_OSP",
        "dgwesp_ISP",
        "ctriple",
    ],
}
LADDER["M4c_nomut"] = [t for t in LADDER["M4c"] if t != "mutual"]
LADDER["M5"] = LADDER["M4c"] + ["nodematch_party", "nodematch_state", "absdiff_nominate"]
LADDER["M6"] = LADDER["M5"] + ["nodeocov_majority", "nodeocov_seniority"]
LADDER["TT"] = ["edges", "ttriple"]


def design(Y, terms, cov=None):
    cs = change_stats(Y, terms, cov)
    n = Y.shape[0]
    mask = ~np.eye(n, dtype=bool)
    X = np.stack([cs[t][mask] for t in terms], 1)
    return X, Y[mask].astype(float), cs


def mple(X, y, ridge=1e-8):
    """Unpenalised logistic MPLE (tiny ridge for numerical stability)."""
    sc = X.std(0)
    sc[sc == 0] = 1.0
    Xs = X / sc

    def f(b):
        eta = Xs @ b
        ll = y * eta - np.logaddexp(0, eta)
        p = 1 / (1 + np.exp(-eta))
        return -(ll.sum()) + ridge * b @ b, -(Xs.T @ (y - p)) + 2 * ridge * b

    def h(b):
        p = 1 / (1 + np.exp(-(Xs @ b)))
        w = p * (1 - p)
        return (Xs * w[:, None]).T @ Xs + 2 * ridge * np.eye(len(b))

    b0 = np.zeros(X.shape[1])
    res = minimize(f, b0, jac=True, hess=h, method="trust-exact", options={"gtol": 1e-8})
    return res.x / sc, res


def conditional_probs(Y, terms, theta, cov=None):
    cs = change_stats(Y, terms, cov)
    eta = sum(theta[k] * cs[t] for k, t in enumerate(terms))
    P = 1 / (1 + np.exp(-eta))
    np.fill_diagonal(P, np.nan)
    return P, eta


def stat_vector(Y, terms, cov=None, decay=DECAY):
    """Full sufficient statistics g(Y) (used by exact joint footprint scores)."""
    A = Y.astype(np.float64)
    g = []
    dout, din = A.sum(1), A.sum(0)
    for t in terms:
        if t == "edges":
            g.append(A.sum())
        elif t == "mutual":
            g.append((A * A.T).sum() / 2)
        elif t == "gwodegree":
            g.append(_gw_f(dout, decay).sum())
        elif t == "gwidegree":
            g.append(_gw_f(din, decay).sum())
        elif t == "dgwesp_OTP":
            g.append((A * _gw_f(A @ A, decay)).sum())
        elif t == "dgwesp_OSP":
            C = A @ A.T
            np.fill_diagonal(C, 0)
            g.append((A * _gw_f(C, decay)).sum())
        elif t == "dgwesp_ISP":
            C = A.T @ A
            np.fill_diagonal(C, 0)
            g.append((A * _gw_f(C, decay)).sum())
        elif t == "ttriple":
            C = A @ A
            g.append((A * C).sum())
        elif t == "ctriple":
            g.append(np.trace(A @ A @ A) / 3)
        elif t == "nodematch_party":
            p = cov["party"]
            g.append((A * (p[:, None] == p[None, :])).sum())
        elif t == "nodematch_state":
            s = cov["state"]
            g.append((A * (s[:, None] == s[None, :])).sum())
        elif t == "absdiff_nominate":
            z = cov["nominate"]
            g.append((A * np.abs(z[:, None] - z[None, :])).sum())
        elif t == "nodeocov_majority":
            g.append((A.sum(1) * cov["majority"]).sum())
        elif t == "nodeocov_seniority":
            g.append((A.sum(1) * cov["seniority"]).sum())
        else:
            raise KeyError(t)
    return np.array(g)
