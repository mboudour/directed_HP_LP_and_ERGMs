# ruff: noqa: E501
"""Role-labelled higher-order ERGM: the initiator of a hyperarc given its participants.

The incidence network of actors and records carries a role on every tie (initiator or
supporter). Statistics of the role-labelled network:
  sponsoring   sum_i log(a_i!)            a_i: number of records initiated by i
  supporting   sum_i log(c_i!)            c_i: number of records supported by i
  directed     sum_{i != k} log(W_ik!)    W_ik: number of records of initiator i supported by k
  reciprocity  sum_{i < k} W_ik W_ki
Conditional on the participants P of a record, exactly one member is the initiator. The
change in the statistics when member v takes the initiator role, relative to the network
without the record, is
  [log(1+a_v), -log(1+c_v), sum_{k in P\\v} log(1+W_vk), sum_{k in P\\v} W_kv]
up to terms that do not depend on v. The probability that v is the initiator is a
multinomial logit in these change statistics (a multinomial pseudolikelihood, since the
statistics of other records are held fixed), estimated over the training records.
"""

import numpy as np

TERMS = ["sponsoring", "supporting", "directed", "reciprocity"]


def counts(records, weights, n):
    a, c, W = np.zeros(n), np.zeros(n), np.zeros((n, n))
    for (s, H), w in zip(records, weights, strict=True):
        a[s] += w
        Hl = list(H)
        c[Hl] += w
        W[s, Hl] += w
    return a, c, W


def features(a, c, W, P, exclude=None):
    """Change statistics for each member of P; exclude=(s, H) removes one record of it."""
    P = list(P)
    a, c = a.copy(), c.copy()
    if exclude is not None:
        s, H = exclude
        a[s] -= 1
        c[list(H)] -= 1
    X = []
    for v in P:
        others = [k for k in P if k != v]
        Wv = W[v, others].copy()
        Wr = W[others, v].copy()
        if exclude is not None:
            s, H = exclude
            if v == s:
                Wv = Wv - 1
            else:
                Wr = Wr - np.array([1.0 if k == s else 0.0 for k in others])
        X.append(
            [
                np.log1p(a[v]),
                -np.log1p(c[v]),
                np.log1p(np.maximum(Wv, 0)).sum(),
                np.maximum(Wr, 0).sum(),
            ]
        )
    return np.array(X)


def fit(records, weights, n, ridge=1e-6, iters=60):
    a, c, W = counts(records, weights, n)
    blocks = []
    for (s, H), w in zip(records, weights, strict=True):
        P = sorted({s, *H})
        X = features(a, c, W, P, exclude=(s, H))
        blocks.append((X, P.index(s), w))
    allX = np.vstack([b[0] for b in blocks])
    sd = allX.std(0) + 1e-12
    th = np.zeros(len(TERMS))
    for _ in range(iters):
        g = -2 * ridge * th
        Hs = -2 * ridge * np.eye(len(TERMS))
        for X, y, w in blocks:
            Z = X / sd
            eta = Z @ th
            p = np.exp(eta - eta.max())
            p /= p.sum()
            zbar = p @ Z
            g += w * (Z[y] - zbar)
            Hs -= w * ((Z * p[:, None]).T @ Z - np.outer(zbar, zbar))
        step = np.linalg.solve(-Hs, g)
        th += step
        if np.max(np.abs(step)) < 1e-8:
            break
    return {"theta": th / sd, "a": a, "c": c, "W": W}


def probs(model, P):
    """Probability that each member of P (in the given order) is the initiator."""
    X = features(model["a"], model["c"], model["W"], P)
    eta = X @ model["theta"]
    p = np.exp(eta - eta.max())
    return p / p.sum()
