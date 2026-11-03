"""Exact maximum likelihood for dyad-independent (p1-type) ERGMs.

A specification whose only dyad-dependent term is mutuality factorizes over
unordered dyads {i, j}. Each dyad takes one of four states, (0,0), (1,0),
(0,1), (1,1), with probabilities proportional to 1, exp(eta_ij), exp(eta_ji)
and exp(eta_ij + eta_ji + rho), where eta_ij = theta' x_ij collects the arc
count, sender, receiver and dyadic covariate terms. The log-likelihood is
concave, and the MLE is found by Newton-Raphson
(Holland and Leinhardt 1981; Fienberg and Wasserman 1981).

The coefficient vector is ordered as ergm.expand_terms(terms, n), so the fit
can be passed to ergm.conditional_probs.
"""

import ergm
import numpy as np
from scipy import sparse as sp


def _dyad_design(n, terms, cov, allowed=None):
    names = ergm.expand_terms(terms, n)
    p = len(names)
    km = names.index("mutual")
    base = [t for t in terms if t not in ("sender", "receiver", "mutual")]
    cs = ergm.change_stats(np.zeros((n, n), np.int8), base, cov)
    iu, ju = np.triu_indices(n, 1)
    if allowed is not None:
        keep = allowed[iu, ju]
        iu, ju = iu[keep], ju[keep]
    m = len(iu)
    col = {t: k for k, t in enumerate(names)}

    def arc_matrix(a, b):
        rows, cols, vals = [], [], []
        for t in base:
            rows.append(np.arange(m))
            cols.append(np.full(m, col[t]))
            vals.append(cs[t][a, b])
        if "sender" in terms:
            keep = a > 0
            rows.append(np.arange(m)[keep])
            cols.append(np.array([col[f"sender_{k}"] for k in a[keep]], int))
            vals.append(np.ones(keep.sum()))
        if "receiver" in terms:
            keep = b > 0
            rows.append(np.arange(m)[keep])
            cols.append(np.array([col[f"receiver_{k}"] for k in b[keep]], int))
            vals.append(np.ones(keep.sum()))
        return sp.csr_matrix(
            (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(m, p)
        )

    S1 = arc_matrix(iu, ju)  # arc i -> j
    S2 = arc_matrix(ju, iu)  # arc j -> i
    E = sp.csr_matrix((np.ones(m), (np.arange(m), np.full(m, km))), shape=(m, p))
    S3 = (S1 + S2 + E).tocsr()
    return names, iu, ju, S1, S2, S3


def fit(Y, terms, cov=None, ridge=1e-6, iters=200, tol=1e-9, allowed=None):
    """Return (theta, info) for the exact MLE of a p1-type specification.

    allowed: optional symmetric boolean matrix; dyads with allowed[i, j] False are
    structural zeros (for example, legislators whose service did not overlap)
    and are excluded from the likelihood.
    """
    n = Y.shape[0]
    names, iu, ju, S1, S2, S3 = _dyad_design(n, terms, cov, allowed)
    a, b = Y[iu, ju].astype(bool), Y[ju, iu].astype(bool)
    state = np.where(a & b, 3, np.where(a, 1, np.where(b, 2, 0)))
    Ss = [None, S1, S2, S3]
    obs = sum((Ss[k][state == k].sum(0).A1 if (state == k).any() else 0) for k in (1, 2, 3))
    p = len(names)
    theta = np.zeros(p)

    def loglik(th):
        e = np.stack([np.zeros(len(iu)), S1 @ th, S2 @ th, S3 @ th], 1)
        lz = np.logaddexp.reduce(e, 1)
        return float(e[np.arange(len(iu)), state].sum() - lz.sum() - ridge * th @ th), e, lz

    ll, e, lz = loglik(theta)
    for it in range(iters):  # noqa: B007 (used after the loop)
        pi = np.exp(e - lz[:, None])
        Es = (sp.diags(pi[:, 1]) @ S1 + sp.diags(pi[:, 2]) @ S2 + sp.diags(pi[:, 3]) @ S3).tocsr()
        g = obs - Es.sum(0).A1 - 2 * ridge * theta
        H = (
            (S1.T @ sp.diags(pi[:, 1]) @ S1)
            + (S2.T @ sp.diags(pi[:, 2]) @ S2)
            + (S3.T @ sp.diags(pi[:, 3]) @ S3)
        ).toarray() - (Es.T @ Es).toarray()
        H += 2 * ridge * np.eye(p)
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, g, rcond=None)[0]
        t = 1.0
        while True:
            nt = theta + t * step
            nll, ne, nlz = loglik(nt)
            if nll >= ll - 1e-12 or t < 1e-8:
                break
            t /= 2
        theta, gain = nt, nll - ll
        ll, e, lz = nll, ne, nlz
        if abs(gain) < tol * max(1.0, abs(ll)) and np.max(np.abs(g)) < 1e-4:
            break
    pi = np.exp(e - lz[:, None])
    expected_arcs = float((pi[:, 1] + pi[:, 2] + 2 * pi[:, 3]).sum())
    expected_mutual = float(pi[:, 3].sum())
    dout, din = Y.sum(1), Y.sum(0)
    info = {
        "dyads": int(len(iu)),
        "loglik": ll,
        "iterations": it + 1,
        "max_abs_gradient": float(np.max(np.abs(g))),
        "observed_arcs": int(Y.sum()),
        "expected_arcs": expected_arcs,
        "observed_mutual": int((a & b).sum()),
        "expected_mutual": expected_mutual,
        "zero_outdegree": int((dout == 0).sum()),
        "zero_indegree": int((din == 0).sum()),
        "se": _standard_errors(H, names),
        "names": names,
    }
    return theta, info


def _standard_errors(H, names):
    """Standard errors of the non-actor terms from the inverse observed information."""
    try:
        V = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        V = np.linalg.pinv(H)
    return {
        t: float(np.sqrt(max(V[k, k], 0.0)))
        for k, t in enumerate(names)
        if not t.startswith(("sender_", "receiver_"))
    }
