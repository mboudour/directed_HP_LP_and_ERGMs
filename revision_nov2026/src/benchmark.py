"""Event-first masking benchmark for ordered single-sponsor group events.

For each mask: withhold whole event types (MCAR or activity-biased MNAR-out),
build the training projection, fit split-specific MPLE ERGMs, score
candidate footprints in three panels (random, sponsor substitution, role
assignment), and return per-mask metrics plus pair-level survival strata.
"""

import math
import random as _random

import ergm
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

LOCAL = [
    "cn_oi",
    "cn_oo",
    "cn_ii",
    "cn_total",
    "aa_oi",
    "aa_oo",
    "aa_ii",
    "aa_total",
    "reverse",
    "degprod",
    "sponsor_activity",
    "cosponsor_popularity",
    "party_share",
]


# ---------------------------------------------------------------- masks
def make_mask(types, counts, mech, q, rng, n_idx=None):
    N = len(types)
    if mech == "MCAR":
        k = int(math.floor(q * N))
        sel = rng.choice(N, size=k, replace=False)
        m = np.zeros(N, bool)
        m[sel] = True
        return m
    if mech == "MNAR-out":
        # a_s(e): full cap-eligible outgoing recipient incidence of the sponsor
        inc = {}
        for (s, H), c in zip(types, counts, strict=False):
            inc[s] = inc.get(s, 0) + c * len(H)
        a = np.array([inc[s] for s, H in types], float)
        lo, hi = 0.0, 1.0 / a.min()
        for _ in range(200):
            lam = (lo + hi) / 2
            if np.minimum(1, lam * a).mean() < q:
                lo = lam
            else:
                hi = lam
        pi = np.minimum(1, lam * a)
        return rng.random(N) < pi
    raise ValueError(mech)


# ---------------------------------------------------------------- local stats
def local_matrices(Y, cov):
    A = Y.astype(float)
    dout, din = A.sum(1), A.sum(0)
    OI = A @ A
    OO = A @ A.T
    np.fill_diagonal(OO, 0)
    II = A.T @ A
    np.fill_diagonal(II, 0)

    def w(d):
        d = np.asarray(d, float)
        with np.errstate(divide="ignore"):
            return np.where(d > 1, 1 / np.log(np.where(d > 1, d, 2)), 0.0)

    aa_oi = (A * w(dout + din)[None, :]) @ A
    aa_oo = (A * w(din)[None, :]) @ A.T
    np.fill_diagonal(aa_oo, 0)
    aa_ii = A.T @ (A * w(dout)[:, None])
    np.fill_diagonal(aa_ii, 0)
    M = {
        "cn_oi": OI,
        "cn_oo": OO,
        "cn_ii": II,
        "cn_total": OI + OO + II,
        "aa_oi": aa_oi,
        "aa_oo": aa_oo,
        "aa_ii": aa_ii,
        "aa_total": aa_oi + aa_oo + aa_ii,
        "reverse": A.T.copy(),
        "degprod": np.outer(dout, din),
        "sponsor_activity": np.repeat(dout[:, None], len(dout), 1),
        "cosponsor_popularity": np.repeat(din[None, :], len(din), 0),
        "party_share": (cov["party"][:, None] == cov["party"][None, :]).astype(float),
    }
    return M


def lift_mean(Mx, s, H):
    return float(Mx[s, list(H)].mean())


# ---------------------------------------------------------------- panels
def reach2(Y):
    """Boolean matrix: weak distance <= 2 in the training projection."""
    U = ((Y + Y.T) > 0).astype(np.int32)
    R = (U + U @ U) > 0
    np.fill_diagonal(R, True)
    return R


def is_local(R, participants):
    p = list(participants)
    return bool(R[np.ix_(p, p)].all())


def random_negative(
    s, H, n, complete, rng, R, used, serve_ok=None, dates=None, max_attempts=200000
):
    k = len(H)
    for _ in range(max_attempts):
        pick = rng.choice(n, size=k + 1, replace=False)
        s2, H2 = int(pick[0]), frozenset(int(x) for x in pick[1:])
        key = (s2, H2)
        if key in complete or key in used:
            continue
        if not is_local(R, pick):
            continue
        if serve_ok is not None and not serve_ok(pick, dates):
            continue
        used.add(key)
        return s2, H2
    return None


def substitution(s, H, complete, rng, R, used):
    elig = []
    for h in sorted(H):
        H2 = frozenset((H - {h}) | {s})
        key = (h, H2)
        if key in complete or key in used:
            continue
        if is_local(R, H | {s}):
            elig.append(key)
    if not elig:
        return None
    key = elig[int(rng.integers(len(elig)))]
    used.add(key)
    return key


# ---------------------------------------------------------------- metrics
def pr_roc(pos, neg):
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    sc = np.r_[pos, neg]
    return average_precision_score(y, sc), roc_auc_score(y, sc)


def role_metrics(scores, true_idx):
    """Expected top-1 and reciprocal rank under random tie-breaking."""
    sc = np.asarray(scores)
    t = sc[true_idx]
    g = (sc > t).sum()
    e = (sc == t).sum()  # includes the true candidate
    top1 = 1.0 / e if g == 0 else 0.0
    rr = np.mean([1.0 / (g + k) for k in range(1, e + 1)])
    return top1, rr


# ---------------------------------------------------------------- one mask
def run_mask(
    types,
    counts,
    idx_types,
    n,
    cov,
    mech,
    q,
    seed,
    models,
    complete,
    with_role=True,
    Ycomplete=None,
    serve_ok=None,
    type_dates=None,
):
    rng = np.random.default_rng(seed)
    m = make_mask(types, counts, mech, q, rng)
    obs = [t for t, mm in zip(idx_types, m, strict=False) if not mm]
    held = [t for t, mm in zip(idx_types, m, strict=False) if mm]
    Y = np.zeros((n, n), np.int8)
    for s, H in obs:
        Y[s, list(H)] = 1
    full_arcs = int(Ycomplete.sum()) if Ycomplete is not None else None
    info = {
        "mech": mech,
        "seed": seed,
        "types_withheld": float(m.mean()),
        "records_withheld": float((np.array(counts) * m).sum() / np.sum(counts)),
        "arc_removal": (1 - Y.sum() / full_arcs) if full_arcs else None,
    }
    Lm = local_matrices(Y, cov)
    P = {}
    theta = {}
    for name in models:
        terms = ergm.LADDER[name]
        X, yv, _ = ergm.design(Y, terms, cov)
        th, res = ergm.mple(X, yv)
        theta[name] = th
        P[name], _ = ergm.conditional_probs(Y, terms, th, cov)

    def score_all(s, H):
        out = {k: lift_mean(Lm[k], s, H) for k in LOCAL}
        Hl = list(H)
        for name in models:
            p = np.clip(P[name][s, Hl], 1e-300, 1)
            out[f"{name}_L1"] = float(p.mean())
            out[f"{name}_L1g"] = float(np.exp(np.log(p).mean()))
            out[f"{name}_L2"] = float(np.exp(np.log(p).sum()))
        return out

    def survives(s, H):
        return bool(Y[s, list(H)].all())

    R = reach2(Y)
    held = [(s, H) for (s, H) in held if is_local(R, H | {s})]
    info["eligible_heldout"] = len(held)
    rand_pos, rand_neg, sub_pos, sub_neg, strata, role = [], [], [], [], [], []
    used_r, used_s = set(), set()
    rand_flags, sub_flags = [], []
    for s, H in held:
        sp = score_all(s, H)
        bip = bool(any(cov["caucus"][h] != cov["caucus"][s] for h in H))
        dates = type_dates.get((s, H)) if type_dates is not None else None
        neg = random_negative(s, H, n, complete, rng, R, used_r, serve_ok, dates)
        if neg is not None:
            rand_pos.append(sp)
            rand_neg.append(score_all(*neg))
            rand_flags.append(bip)
        sub = substitution(s, H, complete, rng, R, used_s)
        if sub is not None:
            h, Hs = sub
            sn = score_all(h, Hs)
            sub_pos.append(sp)
            sub_neg.append(sn)
            sub_flags.append(bip)
            strata.append((survives(s, H), survives(h, Hs)))
        if with_role:
            Pset = sorted(H | {s})
            cands = [score_all(p, frozenset(Pset) - {p}) for p in Pset]
            role.append((cands, Pset.index(s)))
    keys = list(rand_pos[0])
    res = {"info": info, "theta": {k: v.tolist() for k, v in theta.items()}}
    res["random"] = {k: pr_roc([d[k] for d in rand_pos], [d[k] for d in rand_neg]) for k in keys}
    res["substitution"] = {
        k: pr_roc([d[k] for d in sub_pos], [d[k] for d in sub_neg]) for k in keys
    }
    # survival strata: probability true > substitute (ties 0.5)
    st = np.array(strata)
    res["strata_share"] = {
        "true_survives": float(st[:, 0].mean()),
        "sub_survives": float(st[:, 1].mean()),
        "true_only": float((st[:, 0] & ~st[:, 1]).mean()),
        "sub_only": float((~st[:, 0] & st[:, 1]).mean()),
        "both": float((st[:, 0] & st[:, 1]).mean()),
        "neither": float((~st[:, 0] & ~st[:, 1]).mean()),
    }
    win = {}
    for k in keys:
        a = np.array([d[k] for d in sub_pos])
        b = np.array([d[k] for d in sub_neg])
        wv = (a > b) + 0.5 * (a == b)
        win[k] = {
            name: (float(wv[sel].mean()) if sel.any() else None)
            for name, sel in [
                ("true_only", st[:, 0] & ~st[:, 1]),
                ("sub_only", ~st[:, 0] & st[:, 1]),
                ("both", st[:, 0] & st[:, 1]),
                ("neither", ~st[:, 0] & ~st[:, 1]),
            ]
        }
    res["strata_win"] = win
    if with_role:
        rm = {}
        for k in keys:
            t1, rr = zip(
                *[role_metrics([c[k] for c in cands], ti) for cands, ti in role], strict=False
            )
            rm[k] = (float(np.mean(t1)), float(np.mean(rr)))
        sizes = [len(c) for c, _ in role]
        rm["uniform"] = (
            float(np.mean([1 / z for z in sizes])),
            float(np.mean([np.mean([1 / r for r in range(1, z + 1)]) for z in sizes])),
        )
        res["role"] = rm
    # bipartisan / single-party split (caucus-based)
    res["bipartisan"] = {}
    for panel, pos, neg, fl in [
        ("random", rand_pos, rand_neg, rand_flags),
        ("substitution", sub_pos, sub_neg, sub_flags),
    ]:
        fl = np.array(fl)
        res["bipartisan"][panel] = {"share_bipartisan": float(fl.mean())}
        for lab, sel in [("bipartisan", fl), ("single_party", ~fl)]:
            if sel.sum() > 1:
                res["bipartisan"][panel][lab] = {
                    k: pr_roc(
                        [d[k] for d, z in zip(pos, sel, strict=False) if z],
                        [d[k] for d, z in zip(neg, sel, strict=False) if z],
                    )
                    for k in keys
                }
    res["n_pairs"] = {"random": len(rand_pos), "substitution": len(sub_pos), "role": len(role)}
    return res


# ================================================================ case-based split runner


def substitution_pairs(case, positives, R, mech, replicate, seed_base=20261013):
    """Exact replica of the published sponsor-substitution pairing."""
    rnd = _random.Random(seed_base + 20_011 * replicate + (0 if mech == "MCAR" else 10_009))
    names = case.nodes
    used, out = set(), []
    for s, H in positives:
        alts = []
        for h in H:
            H2 = frozenset((H - {h}) | {s})
            key = (h, H2)
            if key in case.complete or key in used:
                continue
            if R[np.ix_(list(H | {s}), list(H | {s}))].all():
                skey = ((names[h],), tuple(sorted(names[x] for x in H2)))
                alts.append((skey, key))
        if alts:
            _, key = rnd.choice(sorted(alts, key=lambda a: a[0]))
            out.append(((s, H), key))
            used.add(key)
    return out


def run_split(case, mech, replicate, models, with_role=True, joint=None):
    m, seed = case.mask(mech, replicate)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    for (s, H), mm in zip(case.types, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
    if getattr(case, "train_uncapped", False):
        for s, H in case.noncap:
            Y[s, list(H)] = 1
    full = case.Ycap
    info = {
        "case": case.name,
        "mech": mech,
        "replicate": replicate,
        "seed": seed,
        "types_withheld": float(m.mean()),
        "records_withheld": float((np.array(case.counts) * m).sum() / np.sum(case.counts)),
        "arc_removal": float(1 - Y.sum() / full.sum()),
    }
    R = reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
    info["eligible_heldout"] = len(pos)
    info["heldout"] = len(held)
    info["surviving_footprints"] = int(sum(Y[s, list(H)].all() for s, H in held))
    cov = case.cov
    Lm = local_matrices(Y, cov)
    P, theta = {}, {}
    for name in models:
        terms = ergm.LADDER[name]
        X, yv, _ = ergm.design(Y, terms, cov)
        th, res = ergm.mple(X, yv)
        theta[name] = th.tolist()
        P[name], _ = ergm.conditional_probs(Y, terms, th, cov)

    def score_all(s, H):
        Hl = sorted(H)
        out = {k: float(Lm[k][s, Hl].mean()) for k in LOCAL}
        for name in models:
            p = np.clip(P[name][s, Hl], 1e-300, 1)
            out[f"{name}_L1"] = float(p.mean())
            out[f"{name}_L1g"] = float(np.exp(np.log(p).mean()))
            out[f"{name}_L2"] = float(np.exp(np.log(p).sum()))
        if joint is not None:
            for name in joint:
                out[f"{name}_LJ"] = joint_footprint_logprob(
                    Y, s, Hl, ergm.LADDER[name], np.array(theta[name]), cov
                )
        return out

    negs, audit = case.random_negatives(pos, R, mech, replicate)
    info["neg_audit"] = dict(audit)
    rand = [
        (score_all(*p), score_all(*q), p) for p, q in zip(pos, negs, strict=False) if q is not None
    ]
    subs = substitution_pairs(case, pos, R, mech, replicate)
    sub = []
    for p, q in subs:
        sub.append(
            (
                score_all(*p),
                score_all(*q),
                p,
                bool(Y[p[0], list(p[1])].all()),
                bool(Y[q[0], list(q[1])].all()),
            )
        )
    role = []
    if with_role:
        for s, H in pos:
            Pset = sorted(H | {s})
            role.append(([score_all(x, frozenset(Pset) - {x}) for x in Pset], Pset.index(s)))
    return {"info": info, "theta": theta, "random": rand, "sub": sub, "role": role}


def joint_footprint_logprob(Y, s, Hl, terms, theta, cov):
    """log Pr(Y_F = 1 | Y_-F) by exact enumeration of the 2^|F| footprint configurations."""
    k = len(Hl)
    Y0 = Y.copy()
    Y0[s, Hl] = 0
    # enumerate configurations in Gray-code order using single-dyad change statistics
    # computed on the current graph (exact, since each step toggles one dyad).
    cur = Y0.copy()
    logw = 0.0
    weights = {0: 0.0}
    state = 0
    for step in range(1, 2**k):
        bit = (step & -step).bit_length() - 1
        j = Hl[bit]
        on = not cur[s, j]
        cs = _single_change(cur, s, j, terms, cov)
        delta = float(theta @ cs)
        logw = logw + (delta if on else -delta)
        cur[s, j] = 1 if on else 0
        state ^= 1 << bit
        weights[state] = logw
    vals = np.array(list(weights.values()))
    lz = np.logaddexp.reduce(vals)
    return float(weights[2**k - 1] - lz)


def _single_change(A, i, j, terms, cov, decay=None):
    """Change statistics for one dyad (i,j) on graph A, ignoring the current value of A[i,j]."""
    decay = ergm.DECAY if decay is None else decay
    A = A.astype(np.float64)
    A[i, j] = 0
    r = 1 - np.exp(-decay)
    out = []
    for t in terms:
        if t == "edges":
            out.append(1.0)
        elif t == "mutual":
            out.append(A[j, i])
        elif t == "gwodegree":
            out.append(r ** A[i].sum())
        elif t == "gwidegree":
            out.append(r ** A[:, j].sum())
        elif t == "dgwesp_OTP":
            own = ergm._gw_f(A[i] @ A[:, j], decay)
            ls = np.nonzero(A[i] * A[j])[0]  # arcs i->l with j->l
            t1 = (r ** (A[i] @ A[:, ls])).sum() if len(ls) else 0.0
            ls2 = np.nonzero(A[:, i] * A[:, j])[0]  # arcs l->j with l->i
            t2 = (r ** (A[ls2] @ A[:, j])).sum() if len(ls2) else 0.0
            out.append(own + t1 + t2)
        elif t == "dgwesp_OSP":
            own = ergm._gw_f(A[i] @ A[j], decay)
            ls = np.nonzero(A[i] * A[:, j])[0]  # arcs i->l, l->j
            ta = (r ** (A[ls] @ A[i])).sum() if len(ls) else 0.0
            ls2 = np.nonzero(A[:, i] * A[:, j])[0]  # arcs l->i, l->j
            tb = (r ** (A[ls2] @ A[i])).sum() if len(ls2) else 0.0
            out.append(own + ta + tb)
        elif t == "dgwesp_ISP":
            own = ergm._gw_f(A[:, i] @ A[:, j], decay)
            ls = np.nonzero(A[j] * A[i])[0]  # arcs j->l, i->l
            ta = (r ** (A[:, j] @ A[:, ls])).sum() if len(ls) else 0.0
            ls2 = np.nonzero(A[:, j] * A[i])[0]  # arcs l->j, i->l
            tb = (r ** (A[:, ls2].T @ A[:, j])).sum() if len(ls2) else 0.0
            out.append(own + ta + tb)
        elif t == "ctriple":
            out.append(A[j] @ A[:, i])
        elif t == "nodematch_party":
            out.append(float(cov["party"][i] == cov["party"][j]))
        elif t == "nodematch_state":
            out.append(float(cov["state"][i] == cov["state"][j]))
        elif t == "absdiff_nominate":
            out.append(abs(cov["nominate"][i] - cov["nominate"][j]))
        elif t == "nodeocov_majority":
            out.append(cov["majority"][i])
        elif t == "nodeocov_seniority":
            out.append(cov["seniority"][i])
        else:
            raise KeyError(t)
    return np.array(out)
