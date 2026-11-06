# ruff: noqa: E501
"""Two-mode ERGM (HM) of the incidence network of candidates and batches, for campaign contributions.

Every batch has exactly one committee, so the ties of committees to batches are fixed and the model
is an ERGM for the ties of candidates to batches, conditional on the committee of each batch. The
change statistic of the tie (i, b) of candidate i to batch b with committee s and other recipients
K = H minus i, with the rest of the network fixed (counts exclude b), is
  edges        1
  activity     log(1 + d_i)                         d_i: training batches received by i
  size         log(1 + |K|)
  closure_c    log(1 + w_si)                        w_si: batches from s to i
  closure_k    sum_{k in K} log(1 + a_ik)           a_ik: batches received by both i and k
  state_c      1[i in the state of s]
  state_k      sum_{k in K} 1[same state]
  dist_c       |ideology of s - CFscore of i|       committee ideology from its training recipients
  dist_k       sum_{k in K} |CFscore difference|
Parameters are estimated by maximum pseudolikelihood with case-control sampling of non-ties: for
each training batch type, all its ties and 20 candidates drawn among the other active candidates,
weighted by the inverse sampling fraction and by the multiplicity of the type. A candidate batch
(s, H) is scored by the geometric mean over h in H of the conditional tie probabilities.
HM0 omits the two closure terms.

The random, party-matched and head-perturbation pairs are those of run_fec.py for the same masks
(alignment checked through the weighted pair count).

Usage: python run_hm_fec.py FEC_DIR DIME CYCLE FEC_RESULTS_DIR OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import fec_case as F
import numpy as np
import run_fec as R
from run_member_fec import seed_of

TERMS = ["edges", "activity", "size", "closure_c", "closure_k", "state_c", "state_k", "dist_c", "dist_k"]
TERMS0 = [t for t in TERMS if not t.startswith("closure")]
N_NEG = 20


def wlogit(X, y, w, ridge=1e-6, iters=60):
    mu, sd = X.mean(0), X.std(0)
    sd[0], mu[0] = 1.0, 0.0
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    th = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z @ th)))
        g = Z.T @ (w * (y - p)) - 2 * ridge * th
        H = (Z * (w * p * (1 - p))[:, None]).T @ Z + 2 * ridge * np.eye(len(th))
        step = np.linalg.solve(H, g)
        th += step
        if np.max(np.abs(step)) < 1e-8:
            break
    beta = th / sd
    beta[0] = th[0] - (th[1:] * mu[1:] / sd[1:]).sum()
    return beta


class Stats:
    def __init__(self, case, W, A, d, ideo):
        self.W, self.A, self.d = W, A, d
        self.lW, self.lA = np.log1p(W), np.log1p(A)
        self.cst, self.kst = case.comm_state, case.cand_state
        self.cf, self.ideo = case.cand_cf, ideo
        self.same_kk = (self.kst[:, None] == self.kst[None, :]).astype(float)

    def rows(self, s, K, cands, own=None):
        """Change statistics of the ties of the candidates `cands` to the batch (s, K + {c}).
        own: boolean array, True where the tie is observed in training (counts then exclude b)."""
        cands = np.asarray(cands)
        K = list(K)
        own = np.zeros(len(cands), bool) if own is None else own
        sub = own.astype(float)
        X = np.empty((len(cands), len(TERMS)))
        X[:, 0] = 1
        X[:, 1] = np.log1p(self.d[cands] - sub)
        X[:, 2] = np.log1p(len(K))
        X[:, 3] = np.log1p(np.maximum(self.W[s, cands] - sub, 0))
        if K:
            Ak = self.A[np.ix_(cands, K)] - sub[:, None]
            X[:, 4] = np.log1p(np.maximum(Ak, 0)).sum(1)
            X[:, 6] = self.same_kk[np.ix_(cands, K)].sum(1)
            X[:, 8] = np.abs(self.cf[cands][:, None] - self.cf[K][None, :]).sum(1)
        else:
            X[:, 4] = X[:, 6] = X[:, 8] = 0
        X[:, 5] = (self.kst[cands] == self.cst[s]).astype(float)
        X[:, 7] = np.abs(self.ideo[s] - self.cf[cands])
        return X


def fit(case, m, seed):
    Y, W, bills = F.training(case, m)
    lean, ideo, align, dist = R.covariates(case, Y)
    Bh_rows, Bh_cols, Bh_w = [], [], []
    types = []
    r = 0
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if mm:
            continue
        types.append((int(s), sorted(int(h) for h in H), float(c)))
        for h in H:
            Bh_rows.append(r)
            Bh_cols.append(h)
            Bh_w.append(float(c))
        r += 1
    from scipy import sparse as sp

    B = sp.csr_matrix((np.ones(len(Bh_rows)), (Bh_rows, Bh_cols)), shape=(r, case.K))
    wv = np.array([c for *_, c in types])
    A = (B.T @ sp.diags(wv) @ B).toarray()
    d = np.diag(A).copy()
    np.fill_diagonal(A, 0)
    st = Stats(case, W, A, d, ideo)
    active = np.flatnonzero(Y.sum(0) > 0)
    rng = np.random.default_rng(seed)
    Xs, ys, ws = [], [], []
    for s, H, c in types:
        Hs = set(H)
        for h in H:
            K = [k for k in H if k != h]
            Xs.append(st.rows(s, K, [h], own=np.array([True])))
            ys.append(1.0)
            ws.append(c)
        pool = active[~np.isin(active, H)]
        neg = rng.choice(pool, size=min(N_NEG, len(pool)), replace=False)
        Xs.append(st.rows(s, H, neg))
        ys += [0.0] * len(neg)
        ws += [c * len(pool) / len(neg)] * len(neg)
        del Hs
    X = np.vstack(Xs)
    y, w = np.array(ys), np.array(ws)
    th = {"HM": wlogit(X, y, w)}
    keep = [TERMS.index(t) for t in TERMS0]
    th["HM0"] = wlogit(X[:, keep], y, w)
    return st, th, W, Y, lean


def score(st, th, s, H):
    H = sorted(H)
    out = {}
    for name, beta in th.items():
        lp = []
        for h in H:
            K = [k for k in H if k != h]
            x = st.rows(s, K, [h])[0]
            if name == "HM0":
                x = x[[TERMS.index(t) for t in TERMS0]]
            lp.append(-np.logaddexp(0, -float(x @ beta)))
        out[name] = float(np.exp(np.mean(lp)))
    return out


def run_split(case, mech, rep):
    m = F.mask(case, mech, rep)
    st, th, W, Y, lean = fit(case, m, seed=seed_of(case.cycle, mech, rep, "hm_fec"))
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    act_c, act_k = Y.sum(1) > 0, Y.sum(0) > 0
    pos = [t for t in held if act_c[t[0]] and all(act_k[h] for h in t[1])]
    sets = {}
    for kind in ("random", "matched", "perturb"):
        neg = F.negatives(case, pos, Y, mech, rep, kind, lean=lean)
        rows = []
        for p, q in zip(pos, neg, strict=False):
            if q is None:
                continue
            a = score(st, th, *p)
            b = score(st, th, *q)
            a["weighted_footprint"] = float(W[p[0], sorted(p[1])].mean())
            b["weighted_footprint"] = float(W[q[0], sorted(q[1])].mean())
            rows.append((a, b))
        sets[kind] = rows
    theta = {k: dict(zip(TERMS if k == "HM" else TERMS0, v.tolist(), strict=True)) for k, v in th.items()}
    return {"theta": theta, **sets}


def main(fec_dir, dime, cycle, fecres, outdir, reps=10):
    os.makedirs(outdir, exist_ok=True)
    case = F.build_case(fec_dir, dime, int(cycle))
    for mech in os.environ.get("MEMBER_MECHS", "MCAR,MNAR-out").split(","):
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = run_split(case, mech, rep)
            old = pickle.load(open(f"{fecres}/{mech}_{rep:02d}.pkl", "rb"))
            for k in ("random", "matched", "perturb"):
                a = [p[i]["weighted_footprint"] for p in r[k] for i in (0, 1)]
                b = [p[i]["weighted_footprint"] for p in old[k] for i in (0, 1)]
                assert len(a) == len(b) and np.allclose(a, b), (cycle, mech, rep, k)
            pickle.dump(r, open(f, "wb"))
            print(cycle, mech, rep, round(time.time() - t, 1), {k: round(v, 3) for k, v in r["theta"]["HM"].items()}, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], int(a[5]) if len(a) > 5 else 10)
