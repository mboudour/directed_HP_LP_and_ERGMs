"""Aggregate per-split pickles into per-mask metrics and paired contrasts."""

import glob
import pickle

import benchmark
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

BOOT, PERM = 10_000, 20_000


def load(outdir):
    res = {}
    for f in sorted(glob.glob(f"{outdir}/M*_*.pkl")):
        r = pickle.load(open(f, "rb"))
        res[(r["info"]["mech"], r["info"]["replicate"])] = r
    return res


def _ap(pos, neg):
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    sc = np.r_[pos, neg]
    return average_precision_score(y, sc), roc_auc_score(y, sc)


def split_metrics(r, keys, strata=True):
    out = {}
    for panel in ("random", "sub"):
        pairs = r[panel]
        for k in keys:
            pos = [a[k] for a, b, *_ in pairs]
            neg = [b[k] for a, b, *_ in pairs]
            out[(panel, k, "pr_auc")], out[(panel, k, "roc_auc")] = _ap(pos, neg)
        # bipartisan split (caucus of sponsor vs any head member)
    return out


def bip_flags(r, case_caucus):
    f = {}
    for panel in ("random", "sub"):
        f[panel] = np.array(
            [any(case_caucus[h] != case_caucus[p[0]] for h in p[1]) for a, b, p, *_ in r[panel]]
        )
    return f


def panel_metric(pairs, k, sel=None):
    pos = [a[k] for i, (a, b, *_) in enumerate(pairs) if sel is None or sel[i]]
    neg = [b[k] for i, (a, b, *_) in enumerate(pairs) if sel is None or sel[i]]
    return _ap(pos, neg)


def role_metrics(r, keys):
    out = {}
    for k in keys:
        t1, rr = [], []
        for cands, ti in r["role"]:
            a, b = benchmark.role_metrics([c[k] for c in cands], ti)
            t1.append(a)
            rr.append(b)
        out[k] = (np.mean(t1), np.mean(rr))
    sizes = [len(c) for c, _ in r["role"]]
    out["uniform"] = (
        np.mean([1 / z for z in sizes]),
        np.mean([np.mean([1 / q for q in range(1, z + 1)]) for z in sizes]),
    )
    return out


def strata(r, keys):
    st = np.array([(x[3], x[4]) for x in r["sub"]])
    groups = {
        "true_only": st[:, 0] & ~st[:, 1],
        "sub_only": ~st[:, 0] & st[:, 1],
        "both": st[:, 0] & st[:, 1],
        "neither": ~st[:, 0] & ~st[:, 1],
    }
    share = {g: float(m.mean()) for g, m in groups.items()}
    share["true_survives"] = float(st[:, 0].mean())
    share["sub_survives"] = float(st[:, 1].mean())
    win = {}
    for k in keys:
        a = np.array([x[0][k] for x in r["sub"]])
        b = np.array([x[1][k] for x in r["sub"]])
        w = (a > b) + 0.5 * (a == b)
        win[k] = {g: (float(w[m].mean()) if m.any() else np.nan) for g, m in groups.items()}
    return share, win


def paired(d, seed=0):
    """Mean difference, percentile bootstrap CI over masks, sign-flip p-value."""
    d = np.asarray(d, float)
    rng = np.random.default_rng(seed)
    bs = rng.choice(d, size=(BOOT, len(d)), replace=True).mean(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    obs = abs(d.mean())
    flips = rng.choice([-1, 1], size=(PERM, len(d)))
    perm = np.abs((flips * d).mean(1))
    p = (1 + (perm >= obs - 1e-15).sum()) / (PERM + 1)
    return float(d.mean()), float(lo), float(hi), float(p)


def mean_ci(x, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    bs = rng.choice(x, size=(BOOT, len(x)), replace=True).mean(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(x.mean()), float(lo), float(hi)
