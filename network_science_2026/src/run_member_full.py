# ruff: noqa: E501
"""Hidden-supporter task with a full ranking, and NHP-D trained on random alternatives.

Same random hidings, hidden bills, hidden co-sponsors and model fits as run_member.py (same seeds).
For every task, v* is ranked
  full    against every legislator active in the training data outside the bill (s and H excluded)
  twenty  against the 19 alternatives of run_member.py (9 most active, 10 random)
  random  against the 10 random alternatives only
  hard    against the 9 most active alternatives only
NHP-D is trained twice: as in run_member.py (training tasks with the 9 most active and 10 random
alternatives; NHPD_mean, NHPD_maxmin) and with 19 alternatives drawn at random among the active
legislators outside the bill (NHPD_mean_r, NHPD_maxmin_r).

For each task and method the file stores the reciprocal rank (expected over ties under a random
order) and the rank in each comparison, and whether v* is one of the nine most active legislators.

Usage: python run_member_full.py CASE V3_DIR OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import benchmark
import ergm
import hm
import nhpd
import numpy as np
import p1
import runlib
import um
from run_member import N_HARD, N_RAND, make_tasks, seed_of
from run_v3 import MLE_MODELS, fit_mple, overlap_matrix
from run_v4 import supervised_probs


def make_tasks_random(bills, active, n, seed, n_alt=N_HARD + N_RAND):
    rng = np.random.default_rng(seed)
    tasks = []
    for b, (s, H) in enumerate(bills):
        Hs = sorted(H)
        if len(Hs) < 2 or not all(active[v] for v in [s, *Hs]):
            continue
        v = Hs[int(rng.integers(len(Hs)))]
        K = tuple(x for x in Hs if x != v)
        excl = {s, *Hs}
        pool = [x for x in range(n) if active[x] and x not in excl]
        if len(pool) < n_alt:
            continue
        alt = rng.choice(pool, size=n_alt, replace=False).tolist()
        tasks.append((s, K, v, [v, *[int(x) for x in alt]], b))
    return tasks


def rank_of(vals):
    """vals[0] is the target. Expected reciprocal rank and expected rank under random tie-breaking."""
    g = int((vals[1:] > vals[0]).sum())
    t = int((vals[1:] == vals[0]).sum()) + 1
    pos = np.arange(g + 1, g + t + 1)
    return float(np.mean(1 / pos)), float(pos.mean())


def hm_scores(model, Q, cands):
    """Vectorized hm.score for the new events Q + {v}, v in cands."""
    S, deg, pair, th, terms = model["S"], model["deg"], model["pair"], model["theta"], model["terms"]
    Q = list(Q)
    q = len(Q)
    cands = np.asarray(cands)
    tix = {t: i for i, t in enumerate(terms)}
    lS = np.log1p(S)
    # members of Q: base statistics over the other members of Q, plus the candidate
    lp = np.zeros(len(cands))
    for i in Q:
        others = [k for k in Q if k != i]
        eta = th[tix["edges"]] + th[tix["activity"]] * np.log1p(deg[i]) + th[tix["size"]] * np.log1p(q)
        if "closure" in tix:
            eta = eta + th[tix["closure"]] * (lS[i, others].sum() + lS[i, cands])
        for k, M in pair.items():
            if k in tix:
                eta = eta + th[tix[k]] * (M[i, others].sum() + M[i, cands])
        lp += -np.logaddexp(0, -eta)
    eta = th[tix["edges"]] + th[tix["activity"]] * np.log1p(deg[cands]) + th[tix["size"]] * np.log1p(q)
    if "closure" in tix:
        eta = eta + th[tix["closure"]] * lS[np.ix_(cands, Q)].sum(1)
    for k, M in pair.items():
        if k in tix:
            eta = eta + th[tix[k]] * M[np.ix_(cands, Q)].sum(1)
    lp += -np.logaddexp(0, -eta)
    return np.exp(lp / (q + 1))


def run_split(case, mech, rep, allowed, tau_hat):
    m, _ = case.mask(mech, rep)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    bills = np.zeros(n)
    events, weights, train_bills = [], [], []
    Bm, Bh = [], []
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            bills[s] += c
            events.append({s, *H})
            weights.append(c)
            train_bills += [(s, tuple(sorted(H)))] * int(c)
            row = np.zeros(n)
            row[[s, *H]] = np.sqrt(c)
            Bm.append(row)
            rh = np.zeros(n)
            rh[list(H)] = np.sqrt(c)
            Bh.append(rh)
    Bm, Bh = np.array(Bm), np.array(Bh)
    Sc = Bm.T @ Bm
    np.fill_diagonal(Sc, 0)
    A = Bh.T @ Bh
    np.fill_diagonal(A, 0)
    dA = A.sum(1)
    RA = A + (A / np.maximum(dA, 1)[None, :]) @ A
    np.fill_diagonal(RA, 0)
    cosp_count = (Bh**2).sum(0)
    active = (Y.sum(0) + Y.sum(1)) > 0
    held = [(s, tuple(sorted(H))) for (s, H), mm in zip(case.types, m, strict=False) if mm]
    tasks = make_tasks(held, active, cosp_count, n, seed_of(case.name, mech, rep, "member"))
    order = np.argsort(-cosp_count, kind="stable")
    top9 = {int(x) for x in [x for x in order if active[x]][:N_HARD]}
    t0 = time.time()
    P = {}
    cov = case.cov
    ergm.DECAY = tau_hat
    th, _ = fit_mple(Y, ergm.LADDER["M5"], cov)
    P["M5"], _ = ergm.conditional_probs(Y, ergm.LADDER["M5"], th, cov)
    ergm.DECAY = 0.5
    th, _ = p1.fit(Y, MLE_MODELS["S1"], cov, allowed=allowed)
    P["S1"], _ = ergm.conditional_probs(Y, MLE_MODELS["S1"], th, cov)
    P["LR"] = supervised_probs(Y, cov, bills, allowed)
    umod = um.fit(events, n, cov)
    hmod = hm.fit(events, weights, n, cov, hm.TERMS_HM)
    L = benchmark.local_matrices(Y, cov)
    t_ergm = time.time() - t0
    logU = np.log(np.clip(umod["P"], 1e-300, 1))

    full_cands = []
    vecs = []
    for s, K, v, cands, b in tasks:
        excl = {s, *K, v}
        alts = [x for x in range(n) if active[x] and x not in excl]
        C = np.array([v, *alts])
        full_cands.append(C)
        members = [s, *K]
        d = {k: M[s, C] for k, M in P.items()}
        d["UM"] = np.exp(logU[np.ix_(C, members)].mean(1))
        d["HM"] = hm_scores(hmod, members, C)
        d["coparticipation"] = Sc[np.ix_(C, members)].mean(1)
        d["aa_total"] = L["aa_total"][s, C]
        d["weighted_pair"] = W[s, C]
        d["hpra"] = RA[np.ix_(C, list(K))].sum(1)
        d["cocitation"] = A[np.ix_(C, list(K))].sum(1)
        d["indegree"] = np.log1p(cosp_count[C])
        vecs.append(d)
    t1 = time.time()
    nh = nhpd_full(case, mech, rep, train_bills, active, cosp_count, n, tasks, full_cands)
    for i, d in enumerate(vecs):
        for k, arr in nh.items():
            d[k] = arr[i]
    t_nhpd = time.time() - t1
    out = {}
    for i, ((s, K, v, cands, b), C, d) in enumerate(zip(tasks, full_cands, vecs, strict=True)):
        pos = {int(x): j for j, x in enumerate(C)}
        idx20 = [pos[int(c)] for c in cands]
        for k, sc in d.items():
            sc = np.asarray(sc, float)
            r = out.setdefault(k, {"full": [], "twenty": [], "random": [], "hard": []})
            r["full"].append(rank_of(sc))
            r["twenty"].append(rank_of(sc[idx20]))
            r["random"].append(rank_of(sc[[idx20[0], *idx20[N_HARD + 1:]]]))
            r["hard"].append(rank_of(sc[idx20[: N_HARD + 1]]))
    out = {k: {sub: np.array(v) for sub, v in r.items()} for k, r in out.items()}
    info = {"tau_hat": tau_hat, "tasks": len(tasks), "held": len(held), "n_alt_full": float(np.mean([len(C) - 1 for C in full_cands])), "t_ergm": round(t_ergm, 1), "t_nhpd": round(t_nhpd, 1)}
    return {"info": info, "ranks": out, "sponsor": [s for s, *_ in tasks], "target_top9": [t[2] in top9 for t in tasks], "n_full": [len(C) - 1 for C in full_cands]}


def nhpd_full(case, mech, rep, train_bills, active, cosp_count, n, tasks, full_cands):
    import torch

    seed = seed_of(case.name, mech, rep, "nhpd")
    nhpd.set_seed(seed % (2**31))
    rng = np.random.default_rng(seed)
    uniq = sorted(set(train_bills))
    adj, nbr = nhpd.clique_adjacency(uniq, n)
    X = nhpd.node2vec_features(nbr, n, seed=seed % (2**31))
    idx = rng.permutation(len(uniq))
    cut = int(round(0.85 * len(uniq)))
    trb, vab = [uniq[i] for i in idx[:cut]], [uniq[i] for i in idx[cut:]]
    designs = {
        "": (make_tasks(trb, active, cosp_count, n, seed + 1), make_tasks(vab, active, cosp_count, n, seed + 2)),
        "_r": (make_tasks_random(trb, active, n, seed + 3), make_tasks_random(vab, active, n, seed + 4)),
    }

    def rows_of(ts):
        out = []
        for s, K, v, cands, _ in ts:
            for j, c in enumerate(cands):
                out.append((s, (*K, int(c)), 1 if j == 0 else 0))
        return out

    test_rows = []
    for (s, K, v, cands, b), C in zip(tasks, full_cands, strict=True):
        for j, c in enumerate(C):
            test_rows.append((s, (*K, int(c)), 1 if j == 0 else 0))
    chunks = [nhpd.tensorize(test_rows[i : i + 20000]) for i in range(0, len(test_rows), 20000)]
    bounds = np.cumsum([0, *[len(C) for C in full_cands]])
    res = {}
    for suf, (tr, va) in designs.items():
        trd, vad = nhpd.tensorize(rows_of(tr)), nhpd.tensorize(rows_of(va))
        for variant, key in (("mean", "NHPD_mean"), ("maxmin", "NHPD_maxmin")):
            torch.manual_seed(seed % (2**31))
            model = nhpd.NHPD(X.shape[1], variant)
            nhpd.train(model, X, adj, trd, vad, epochs=100)
            sco = np.concatenate([np.asarray(nhpd.scores(model, X, adj, ch)) for ch in chunks])
            res[key + suf] = [sco[bounds[i] : bounds[i + 1]] for i in range(len(full_cands))]
    return res


def main(name, v3dir, outdir, reps=5):
    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    allowed = overlap_matrix(case)
    for rep in range(1, reps + 1):
        for mech in os.environ.get("MEMBER_MECHS", "MCAR,MNAR-out").split(","):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            old = pickle.load(open(f"{v3dir}/{mech}_{rep:02d}.pkl", "rb"))
            r = run_split(case, mech, rep, allowed, old["info"]["tau_hat"])
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, r["info"], round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 5)
