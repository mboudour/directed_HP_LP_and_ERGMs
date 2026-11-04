# ruff: noqa: E501
"""Benchmark on the FEC committee-to-candidate hypergraph (bipartite 2-section).

Models (all fitted to the training 2-section Y of committees x candidates):
  * BS0: logit p_ij = theta + alpha_i + beta_j (committee and candidate effects), exact MLE;
  * BS1: BS0 + partisan alignment, ideological distance, same state, exact MLE;
  * BM:  degree-term model by MPLE: arcs, gwb1degree, gwb2degree, gwb1dsp, gwb2dsp,
         partisan alignment, ideological distance, same state, candidate incumbency and
         Senate seat; decay selected by profile pseudolikelihood (key BM), and decay 0.5
         (key BM_t05);
  * LR:  logistic regression on standardized local features.
Committee partisanship (share of Republican recipients) and ideology (mean DIME CFscore of
recipients) are computed from the training 2-section of each mask only.
Local scores: committee activity, candidate popularity, degree product, three-paths,
item-based collaborative filtering, partisan alignment, ideological proximity, weighted
footprint, observed footprint share, committee bill count.

Usage: python run_fec.py FEC_DIR DIME_PATH CYCLE OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import fec_case as F
import numpy as np
from scipy import sparse as sp
from sklearn.linear_model import LogisticRegression

TAU_GRID = [0.5, 1.0, 2.0, 3.0, 4.0]


def logit_newton(X, y, ridge=1e-6, iters=60, offset=None):
    """Penalized logistic MLE by Newton-Raphson; X scipy sparse or dense."""
    p = X.shape[1]
    th = np.zeros(p)
    dense = not sp.issparse(X)
    for _ in range(iters):
        eta = X @ th
        if offset is not None:
            eta = eta + offset
        mu = 1 / (1 + np.exp(-eta))
        g = X.T @ (y - mu) - 2 * ridge * th
        w = mu * (1 - mu)
        if dense:
            H = (X * w[:, None]).T @ X
        else:
            H = (X.T @ sp.diags(w) @ X).toarray()
        H += 2 * ridge * np.eye(p)
        step = np.linalg.solve(H, g)
        th = th + step
        if np.max(np.abs(step)) < 1e-7:
            break
    return th


def covariates(case, Y):
    rec = Y @ case.cand_rep
    dem = Y @ case.cand_dem
    tot = Y.sum(1)
    lean = np.where(rec + dem > 0, rec / np.maximum(rec + dem, 1), 0.5)
    ideo = np.where(tot > 0, (Y @ case.cand_cf) / np.maximum(tot, 1), np.mean(case.cand_cf))
    align = lean[:, None] * case.cand_rep[None, :] + (1 - lean)[:, None] * case.cand_dem[None, :]
    dist = np.abs(ideo[:, None] - case.cand_cf[None, :])
    return lean, ideo, align, dist


def bipartite_change_stats(Y, tau):
    r = 1 - np.exp(-tau)
    A = Y.astype(float)
    dout = A.sum(1)[:, None] - A
    din = A.sum(0)[None, :] - A
    S = A @ A.T  # committee x committee shared candidates
    T = A.T @ A  # candidate x candidate shared committees
    np.fill_diagonal(S, 0)
    np.fill_diagonal(T, 0)
    RS0, RS1 = r**S, r ** np.maximum(S - 1, 0)
    np.fill_diagonal(RS0, 0)
    np.fill_diagonal(RS1, 0)
    RT0, RT1 = r**T, r ** np.maximum(T - 1, 0)
    np.fill_diagonal(RT0, 0)
    np.fill_diagonal(RT1, 0)
    b1dsp = np.where(A > 0, RS1 @ A, RS0 @ A)  # sum_l Y_lj r^{s_il(-j)}
    b2dsp = np.where(A > 0, A @ RT1, A @ RT0)  # sum_k Y_ik r^{t_jk(-i)}
    return {"gwb1degree": r**dout, "gwb2degree": r**din, "gwb1dsp": b1dsp, "gwb2dsp": b2dsp}


def fit_bm(case, Y, tau, align, dist):
    cs = bipartite_change_stats(Y, tau)
    cols = [
        np.ones_like(align),
        cs["gwb1degree"],
        cs["gwb2degree"],
        cs["gwb1dsp"],
        cs["gwb2dsp"],
        align,
        dist,
        case.same_state,
        np.broadcast_to(case.cand_incumbent[None, :], align.shape),
        np.broadcast_to(case.cand_senate[None, :], align.shape),
    ]
    X = np.stack([c.ravel() for c in cols], 1)
    y = Y.ravel().astype(float)
    th = logit_newton(X, y)
    eta = X @ th
    pl = float((y * eta - np.logaddexp(0, eta)).sum())
    P = (1 / (1 + np.exp(-eta))).reshape(Y.shape)
    return P, th, pl


def fit_bs(case, Y, align, dist, covs=True):
    C, K = Y.shape
    n = C * K
    ii = np.repeat(np.arange(C), K)
    jj = np.tile(np.arange(K), C)
    rows, cols, vals = [np.arange(n)], [np.zeros(n, int)], [np.ones(n)]
    keep_i = ii > 0
    rows.append(np.arange(n)[keep_i])
    cols.append(ii[keep_i])
    vals.append(np.ones(keep_i.sum()))
    keep_j = jj > 0
    rows.append(np.arange(n)[keep_j])
    cols.append(C - 1 + jj[keep_j])
    vals.append(np.ones(keep_j.sum()))
    p = C + K - 1
    if covs:
        for k, c in enumerate([align, dist, case.same_state]):
            rows.append(np.arange(n))
            cols.append(np.full(n, p + k))
            vals.append(c.ravel())
        p += 3
    X = sp.csr_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, p)
    )
    th = logit_newton(X, Y.ravel().astype(float))
    P = (1 / (1 + np.exp(-(X @ th)))).reshape(Y.shape)
    return P, th[-3:] if covs else th[:1]


def local_matrices(case, Y, W, bills, align, dist):
    A = Y.astype(float)
    dout = A.sum(1)[:, None] - A
    din = A.sum(0)[None, :] - A
    P3 = A @ A.T @ A - A * (A.sum(1)[:, None] + A.sum(0)[None, :] - 1)
    T = A.T @ A
    dk = np.maximum(A.sum(0), 1)
    Sim = T / np.sqrt(dk[:, None] * dk[None, :])
    np.fill_diagonal(Sim, 0)
    cf = (A @ Sim) / np.maximum(A.sum(1), 1)[:, None]
    out_full = np.repeat(A.sum(1)[:, None], A.shape[1], 1)
    in_full = np.repeat(A.sum(0)[None, :], A.shape[0], 0)
    return {
        "activity": out_full,
        "popularity": in_full,
        "degprod": out_full * in_full,
        "_dout_excl": dout,
        "_din_excl": din,
        "path3": P3,
        "cofunding": cf,
        "alignment": align,
        "proximity": -dist,
        "weighted_footprint": W,
        "observed_fraction": A,
        "bill_count": np.repeat(bills[:, None], Y.shape[1], 1),
    }


def lr_probs(case, L):
    feats = ["path3", "cofunding", "alignment", "proximity"]
    F_ = (
        [L["_dout_excl"], L["_din_excl"], L["_dout_excl"] * L["_din_excl"]]
        + [L[k] for k in feats]
        + [
            case.same_state,
            np.broadcast_to(case.cand_incumbent[None, :], case.same_state.shape),
            np.broadcast_to(case.cand_senate[None, :], case.same_state.shape),
            np.log1p(L["bill_count"]),
        ]
    )
    X = np.stack([f.ravel() for f in F_], 1)
    X[:, 3] = np.log1p(np.maximum(X[:, 3], 0))  # three-paths
    mu, sd = X.mean(0), X.std(0) + 1e-12
    Xs = (X - mu) / sd
    y = L["observed_fraction"].ravel()
    clf = LogisticRegression(max_iter=3000)
    clf.fit(Xs, y)
    return clf.predict_proba(Xs)[:, 1].reshape(case.same_state.shape)


def run_split(case, mech, rep):
    m = F.mask(case, mech, rep)
    Y, W, bills = F.training(case, m)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    act_c, act_k = Y.sum(1) > 0, Y.sum(0) > 0
    pos = [t for t in held if act_c[t[0]] and all(act_k[h] for h in t[1])]
    lean, ideo, align, dist = covariates(case, Y)
    L = local_matrices(case, Y, W, bills, align, dist)
    P, theta, prof = {}, {}, {}
    for tau in TAU_GRID:
        prof[tau] = fit_bm(case, Y, tau, align, dist)[2]
    tau_hat = max(prof, key=prof.get)
    P["BM"], theta["BM"], _ = fit_bm(case, Y, tau_hat, align, dist)
    P["BM_t05"], theta["BM_t05"], _ = fit_bm(case, Y, 0.5, align, dist)
    P["BS0"], _ = fit_bs(case, Y, align, dist, covs=False)
    P["BS1"], theta["BS1"] = fit_bs(case, Y, align, dist, covs=True)
    P["LR"] = lr_probs(case, L)

    def score(s, H):
        Hl = sorted(H)
        out = {k: float(L[k][s, Hl].mean()) for k in L if not k.startswith("_")}
        for k, Pm in P.items():
            out[k] = float(np.exp(np.log(np.clip(Pm[s, Hl], 1e-300, 1)).mean()))
        return out

    def meta(s, H):
        g = [int(case.cand_group[h]) for h in H]
        lc = int(lean[s] > 0.5)
        cross = sum(1 for x in g if x in (0, 1) and x != lc)
        return {
            "size": len(H),
            "committee": int(s),
            "cross": cross,
            "surv": bool(Y[s, sorted(H)].all()),
        }

    sets = {}
    for kind in ("random", "matched", "perturb"):
        neg = F.negatives(case, pos, Y, mech, rep, kind, lean=lean)
        sets[kind] = [
            (score(*p), score(*q), meta(*p))
            for p, q in zip(pos, neg, strict=False)
            if q is not None
        ]
    return {
        "info": {
            "mech": mech,
            "replicate": rep,
            "heldout": len(held),
            "evaluated": len(pos),
            "tau_hat": tau_hat,
            "tau_profile": prof,
        },
        "theta": {k: np.asarray(v).tolist() for k, v in theta.items()},
        **sets,
    }


def main(fec_dir, dime, cycle, outdir, reps=20):
    os.makedirs(outdir, exist_ok=True)
    case = F.build_case(fec_dir, dime, int(cycle))
    pickle.dump(
        {
            "accounting": case.accounting,
            "C": case.C,
            "K": case.K,
            "cf_missing": case.cand_cf_missing,
        },
        open(f"{outdir}/meta.pkl", "wb"),
    )
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = run_split(case, mech, rep)
            pickle.dump(r, open(f, "wb"))
            print(cycle, mech, rep, r["info"]["tau_hat"], round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4], int(a[5]) if len(a) > 5 else 20)
