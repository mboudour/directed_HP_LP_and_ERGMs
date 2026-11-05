# ruff: noqa: E501
"""Hidden co-sponsor task: rank one hidden co-sponsor of a hidden bill among 20 candidates.

For every random hiding of run_v3 (the same masks), each hidden bill (s, H) with at least two
co-sponsors whose participants are all active in the training data has one co-sponsor v* hidden
(chosen uniformly with a seed fixed by case, mechanism, hiding and bill). Given the sponsor s and
the remaining co-sponsors K = H minus v*, the methods rank v* against 19 non-members of the bill:
the 9 legislators who co-sponsored most training bills and 10 others drawn at random among those
active in the training data, as in the hidden-member design for directed F-hypergraphs.

Methods (all fitted to the training bills of the hiding):
  M5, S1, LR    directed pairwise ERGMs and logistic regression; score P(s -> v)
  UM            undirected pairwise ERGM; geometric mean of P over the pairs of v with s and K
  HM            two-mode ERGM; score of the act {s} + K + {v}
  coparticipation  mean number of training bills shared by v with s and with each member of K
  aa_total      directed Adamic-Adar between s and v
  weighted_pair number of training bills sponsored by s and co-sponsored by v
  hpra          hyperedge resource allocation on the co-sponsor projection A: sum over w in K of (A + A D^-1 A)_vw
  cocitation    sum over w in K of A_vw
  indegree      log(1 + number of training bills co-sponsored by v)
  NHPD_mean, NHPD_maxmin   NHP-D (nhpd.py), trained on the training bills (85% training, 15% validation
                examples built with the same hidden-member rule), node features from the clique
                expansion of all training bills.

Usage: python run_member.py CASE V3_DIR OUTDIR [REPS] [--no-nhpd]
"""

import hashlib
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
from run_v3 import MLE_MODELS, fit_mple, overlap_matrix
from run_v4 import supervised_probs

N_HARD, N_RAND = 9, 10


def seed_of(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:4], "little")


def make_tasks(bills, active, popularity, n, seed):
    """bills: list of (s, H). Returns list of (s, K, target, candidates) with target first in candidates."""
    rng = np.random.default_rng(seed)
    order = np.argsort(-popularity, kind="stable")
    tasks = []
    for b, (s, H) in enumerate(bills):
        Hs = sorted(H)
        if len(Hs) < 2 or not all(active[v] for v in [s, *Hs]):
            continue
        v = Hs[int(rng.integers(len(Hs)))]
        K = tuple(x for x in Hs if x != v)
        excl = {s, *Hs}
        pool = [x for x in order if active[x] and x not in excl]
        if len(pool) < N_HARD + N_RAND:
            continue
        hard = pool[:N_HARD]
        rest = pool[N_HARD:]
        rnd = rng.choice(rest, size=N_RAND, replace=False).tolist()
        tasks.append((s, K, v, [v, *hard, *[int(x) for x in rnd]], b))
    return tasks


def run_split(case, mech, rep, allowed, tau_hat, use_nhpd=True):
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
    popularity = Y.sum(0).astype(float)
    cosp_count = (Bh**2).sum(0)
    active = (Y.sum(0) + Y.sum(1)) > 0
    held = [(s, tuple(sorted(H))) for (s, H), mm in zip(case.types, m, strict=False) if mm]
    tasks = make_tasks(held, active, cosp_count, n, seed_of(case.name, mech, rep, "member"))
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

    def sc(s, K, v):
        out = {k: float(M[s, v]) for k, M in P.items()}
        members = [s, *K]
        out["UM"] = float(np.exp(np.mean(np.log(np.clip(umod["P"][v, members], 1e-300, 1)))))
        out["HM"] = hm.score(hmod, {s, *K, v})
        out["coparticipation"] = float(Sc[v, members].mean())
        out["aa_total"] = float(L["aa_total"][s, v])
        out["weighted_pair"] = float(W[s, v])
        out["hpra"] = float(RA[v, list(K)].sum())
        out["cocitation"] = float(A[v, list(K)].sum())
        out["indegree"] = float(np.log1p(cosp_count[v]))
        return out

    rows = [[sc(s, K, c) for c in cands] for s, K, v, cands, b in tasks]
    info = {"tau_hat": tau_hat, "tasks": len(tasks), "held": len(held), "t_ergm": round(t_ergm, 1)}
    if use_nhpd and tasks:
        t1 = time.time()
        nh = nhpd_scores(case, mech, rep, train_bills, active, cosp_count, n, tasks)
        for k, arr in nh.items():
            for i, r in enumerate(rows):
                for j in range(len(r)):
                    r[j][k] = float(arr[i][j])
        info["t_nhpd"] = round(time.time() - t1, 1)
    return {"info": info, "tasks": [(s, K, v, c, b) for s, K, v, c, b in tasks], "scores": rows, "sponsor": [s for s, *_ in tasks]}


def nhpd_scores(case, mech, rep, train_bills, active, cosp_count, n, tasks):
    import torch

    seed = seed_of(case.name, mech, rep, "nhpd")
    nhpd.set_seed(seed % (2**31))
    rng = np.random.default_rng(seed)
    uniq = sorted(set(train_bills))
    adj, nbr = nhpd.clique_adjacency(uniq, n)
    X = nhpd.node2vec_features(nbr, n, seed=seed % (2**31))
    idx = rng.permutation(len(uniq))
    cut = int(round(0.85 * len(uniq)))
    tr = make_tasks([uniq[i] for i in idx[:cut]], active, cosp_count, n, seed + 1)
    va = make_tasks([uniq[i] for i in idx[cut:]], active, cosp_count, n, seed + 2)

    def rows_of(ts):
        out = []
        for s, K, v, cands, _ in ts:
            for j, c in enumerate(cands):
                out.append((s, (*K, c), 1 if j == 0 else 0))
        return out

    trd, vad = nhpd.tensorize(rows_of(tr)), nhpd.tensorize(rows_of(va))
    ted = nhpd.tensorize(rows_of(tasks))
    res = {}
    for variant, key in (("mean", "NHPD_mean"), ("maxmin", "NHPD_maxmin")):
        torch.manual_seed(seed % (2**31))
        model = nhpd.NHPD(X.shape[1], variant)
        nhpd.train(model, X, adj, trd, vad, epochs=100)
        sco = nhpd.scores(model, X, adj, ted)
        res[key] = sco.reshape(len(tasks), N_HARD + N_RAND + 1)
    return res


def main(name, v3dir, outdir, reps=10, use_nhpd=True):
    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    allowed = overlap_matrix(case)
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            old = pickle.load(open(f"{v3dir}/{mech}_{rep:02d}.pkl", "rb"))
            r = run_split(case, mech, rep, allowed, old["info"]["tau_hat"], use_nhpd)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, r["info"], round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 10, "--no-nhpd" not in sys.argv)
