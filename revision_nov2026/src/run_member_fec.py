# ruff: noqa: E501
"""Hidden-supporter task on the contribution hypergraph (committee -> candidates).

For every random hiding of run_fec (the same masks), each hidden batch (s, H) with at least two
recipients, whose committee and recipients are all active in the training data, has one recipient
v* hidden (seeded by cycle, mechanism, hiding and batch). Given the committee s and the remaining
recipients K, the methods rank v* against 19 candidates outside the batch: the 9 candidates who
received most training batches and 10 others drawn at random among the active candidates.

Methods: BS1, BM (decay selected over the grid of run_fec), LR (run_fec features): P(s -> v);
co-funding similarity, weighted pair count W[s, v], three-paths; co-participation (mean number
of training batches shared by v with s and with each member of K); co-citation and HPRA on the
recipient projection; in-degree; NHP-D-mean and NHP-D-maxmin+ (nhpd.py) on the directed
F-hypergraph with committees and candidates as nodes.

Usage: python run_member_fec.py FEC_DIR DIME CYCLE OUTDIR [REPS] [--no-nhpd]
"""

import hashlib
import os
import pickle
import sys
import time

import fec_case as F
import nhpd
import numpy as np
import run_fec as R
from scipy import sparse as sp

N_HARD, N_RAND = 9, 10
MAX_TRAIN_ARCS = 8000


def seed_of(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:4], "little")


def make_tasks(arcs, cact, kact, received, seed):
    rng = np.random.default_rng(seed)
    order = np.argsort(-received, kind="stable")
    tasks = []
    for b, (s, H) in enumerate(arcs):
        Hs = sorted(H)
        if len(Hs) < 2 or not cact[s] or not all(kact[v] for v in Hs):
            continue
        v = Hs[int(rng.integers(len(Hs)))]
        K = tuple(x for x in Hs if x != v)
        excl = set(Hs)
        pool = [int(x) for x in order if kact[x] and x not in excl]
        if len(pool) < N_HARD + N_RAND:
            continue
        hard = pool[:N_HARD]
        rnd = rng.choice(pool[N_HARD:], size=N_RAND, replace=False).tolist()
        tasks.append((int(s), K, v, [v, *hard, *[int(x) for x in rnd]], b))
    return tasks


def run_split(case, mech, rep, use_nhpd=True):
    m = F.mask(case, mech, rep)
    Y, W, bills = F.training(case, m)
    C, Kn = case.C, case.K
    rows_b, cols_b, vals_b = [], [], []
    train_arcs = []
    r = 0
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if mm:
            continue
        for h in H:
            rows_b.append(r)
            cols_b.append(h)
            vals_b.append(np.sqrt(c))
        train_arcs += [(int(s), tuple(sorted(int(h) for h in H)))] * int(c)
        r += 1
    Bh = sp.csr_matrix((vals_b, (rows_b, cols_b)), shape=(r, Kn))
    A = (Bh.T @ Bh).toarray()
    received = np.diag(A).copy()
    np.fill_diagonal(A, 0)
    dA = A.sum(1)
    RA = A + (A / np.maximum(dA, 1)[None, :]) @ A
    np.fill_diagonal(RA, 0)
    cact, kact = Y.sum(1) > 0, Y.sum(0) > 0
    held = [(int(s), tuple(sorted(H))) for (s, H), mm in zip(case.types, m, strict=False) if mm]
    tasks = make_tasks(held, cact, kact, received, seed_of(case.cycle, mech, rep, "member"))
    t0 = time.time()
    lean, ideo, align, dist = R.covariates(case, Y)
    L = R.local_matrices(case, Y, W, bills, align, dist)
    prof = {tau: R.fit_bm(case, Y, tau, align, dist)[2] for tau in R.TAU_GRID}
    tau_hat = max(prof, key=prof.get)
    P = {"BM": R.fit_bm(case, Y, tau_hat, align, dist)[0], "BS1": R.fit_bs(case, Y, align, dist, covs=True)[0], "LR": R.lr_probs(case, L)}
    t_ergm = time.time() - t0

    def sc(s, K, v):
        out = {k: float(M[s, v]) for k, M in P.items()}
        out["cofunding"] = float(L["cofunding"][s, v])
        out["weighted_pair"] = float(W[s, v])
        out["path3"] = float(L["path3"][s, v])
        out["coparticipation"] = float(np.mean([W[s, v], *A[v, list(K)]]))
        out["hpra"] = float(RA[v, list(K)].sum())
        out["cocitation"] = float(A[v, list(K)].sum())
        out["indegree"] = float(np.log1p(received[v]))
        return out

    rows = [[sc(s, K, c) for c in cands] for s, K, v, cands, b in tasks]
    info = {"tau_hat": tau_hat, "tasks": len(tasks), "held": len(held), "t_models": round(t_ergm, 1)}
    if use_nhpd and tasks:
        t1 = time.time()
        nh, ninfo = nhpd_scores(case, mech, rep, train_arcs, cact, kact, received, tasks)
        for k, arr in nh.items():
            for i, rr in enumerate(rows):
                for j in range(len(rr)):
                    rr[j][k] = float(arr[i][j])
        info["t_nhpd"] = round(time.time() - t1, 1)
        info.update(ninfo)
    return {"info": info, "tasks": tasks, "scores": rows, "sponsor": [s for s, *_ in tasks]}


def nhpd_scores(case, mech, rep, train_arcs, cact, kact, received, tasks):
    import torch

    C = case.C
    n = C + case.K
    seed = seed_of(case.cycle, mech, rep, "nhpd")
    nhpd.set_seed(seed % (2**31))
    rng = np.random.default_rng(seed)
    uniq = sorted(set(train_arcs))
    graph_arcs = [(s, tuple(C + h for h in H)) for s, H in uniq]
    adj, nbr = nhpd.clique_adjacency(graph_arcs, n)
    X = nhpd.node2vec_features(nbr, n, seed=seed % (2**31))
    elig = [a for a in uniq if len(a[1]) >= 2]
    idx = rng.permutation(len(elig))[: int(MAX_TRAIN_ARCS / 0.85)]
    cut = int(round(0.85 * len(idx)))
    tr = make_tasks([elig[i] for i in idx[:cut]], cact, kact, received, seed + 1)
    va = make_tasks([elig[i] for i in idx[cut:]], cact, kact, received, seed + 2)

    def rows_of(ts):
        out = []
        for s, K, v, cands, _ in ts:
            for j, c in enumerate(cands):
                out.append((s, tuple(C + x for x in (*K, c)), 1 if j == 0 else 0))
        return out

    trd, vad, ted = nhpd.tensorize(rows_of(tr)), nhpd.tensorize(rows_of(va)), nhpd.tensorize(rows_of(tasks))
    res = {}
    for variant, key in (("mean", "NHPD_mean"), ("maxmin", "NHPD_maxmin")):
        torch.manual_seed(seed % (2**31))
        model = nhpd.NHPD(X.shape[1], variant)
        nhpd.train(model, X, adj, trd, vad, epochs=100)
        res[key] = nhpd.scores(model, X, adj, ted).reshape(len(tasks), N_HARD + N_RAND + 1)
    return res, {"nhpd_train_arcs": len(tr), "nhpd_valid_arcs": len(va), "graph_arcs": len(uniq)}


def main(fec_dir, dime, cycle, outdir, reps=5, use_nhpd=True):
    os.makedirs(outdir, exist_ok=True)
    case = F.build_case(fec_dir, dime, int(cycle))
    for rep in range(1, reps + 1):
        for mech in os.environ.get("MEMBER_MECHS", "MCAR,MNAR-out").split(","):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = run_split(case, mech, rep, use_nhpd)
            pickle.dump(r, open(f, "wb"))
            print(cycle, mech, rep, r["info"], round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(a[0], a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 5, "--no-nhpd" not in sys.argv)
