# ruff: noqa: E501
"""Temporal forecasting benchmark for campaign contributions.

Batches are assigned to quarters of the two-year cycle by transaction date. A hyperarc
(committee, set of candidates) belongs to the target if all its batches fall in quarters
6-7 (the last six months of the cycle); otherwise it belongs to the training record, and its
batches in quarters 0-5 form the training data. Two stages:

  export  quarterly bipartite committee x candidate networks of quarters 1-5 with lagged edge
          covariates from the earlier quarters (memory, log history count, log lagged committee
          and candidate degrees, log lagged three-paths, lagged co-funding similarity, partisan
          alignment and ideological distance from the lagged committee positions), same state,
          incumbency and Senate candidacy; and the covariates for the forecast window.
  score   reads the btergm forecast, fits B1 and BM and computes the local scores on the
          training record (quarters 0-5), builds the random, party-matched and head-perturbation
          sets for the target hyperarcs, and stores all scores.

Usage: python temporal_fec.py export FEC_DIR DIME CYCLE OUTDIR
       python temporal_fec.py score  FEC_DIR DIME CYCLE OUTDIR
"""

import os
import pickle
import sys

import fec_case as F
import numpy as np
import run_fec as R


def quarter(d, cycle):
    try:
        y, mth = int(d[4:8]), int(d[0:2])
    except ValueError:
        return -1
    return (y - (cycle - 1)) * 4 + (mth - 1) // 3


def batch_quarters(case):
    """Per type: list of quarters of its batches."""
    return [sorted(quarter(d, case.cycle) for d in case.type_dates[t]) for t in case.types]


def nets(case, bq):
    A = np.zeros((8, case.C, case.K))
    for (s, H), qs in zip(case.types, bq, strict=True):
        for q in qs:
            if 0 <= q <= 7:
                A[q, s, list(H)] += 1
    return A


def lagged(case, Hst, last):
    Y = (Hst > 0).astype(np.int8)
    lean, ideo, align, dist = R.covariates(case, Y)
    A = Y.astype(float)
    P3 = A @ A.T @ A - A * (A.sum(1)[:, None] + A.sum(0)[None, :] - 1)
    T = A.T @ A
    dk = np.maximum(A.sum(0), 1)
    Sim = T / np.sqrt(dk[:, None] * dk[None, :])
    np.fill_diagonal(Sim, 0)
    cf = (A @ Sim) / np.maximum(A.sum(1), 1)[:, None]
    C, K = A.shape
    return {
        "memory": (last > 0).astype(float),
        "history": np.log1p(Hst),
        "out_lag": np.log1p(A.sum(1))[:, None] * np.ones((1, K)),
        "in_lag": np.ones((C, 1)) * np.log1p(A.sum(0))[None, :],
        "threepath_lag": np.log1p(np.maximum(P3, 0)),
        "cofunding_lag": cf,
        "alignment_lag": align,
        "distance_lag": dist,
    }


def exo(case):
    C = case.C
    return {
        "same_state": case.same_state,
        "incumbent": np.ones((C, 1)) * case.cand_incumbent[None, :],
        "senate": np.ones((C, 1)) * case.cand_senate[None, :],
    }


def export(fec_dir, dime, cycle, outdir):
    os.makedirs(outdir, exist_ok=True)
    case = F.build_case(fec_dir, dime, int(cycle))
    bq = batch_quarters(case)
    A = nets(case, bq)
    for k, M in exo(case).items():
        np.savetxt(f"{outdir}/exo_{k}.csv", M, delimiter=",", fmt="%.6g")
    for t in range(1, 6):
        np.savetxt(f"{outdir}/net_{t}.csv", (A[t] > 0).astype(int), delimiter=",", fmt="%d")
        for k, M in lagged(case, A[:t].sum(0), A[t - 1]).items():
            np.savetxt(f"{outdir}/lag_{t}_{k}.csv", M, delimiter=",", fmt="%.6g")
    for k, M in lagged(case, A[:6].sum(0), A[5]).items():
        np.savetxt(f"{outdir}/lag_target_{k}.csv", M, delimiter=",", fmt="%.6g")
    tgt = np.array([all(q >= 6 for q in qs) for qs in bq])
    pickle.dump({"target": tgt.tolist()}, open(f"{outdir}/meta.pkl", "wb"))
    print(cycle, "types", len(case.types), "target types", int(tgt.sum()), flush=True)


def score(fec_dir, dime, cycle, outdir):
    case = F.build_case(fec_dir, dime, int(cycle))
    bq = batch_quarters(case)
    m = np.array([all(q >= 6 for q in qs) for qs in bq])
    Y = np.zeros((case.C, case.K), np.int8)
    W = np.zeros((case.C, case.K))
    bills = np.zeros(case.C)
    for (s, H), qs, mm in zip(case.types, bq, m, strict=True):
        if mm:
            continue
        c = sum(1 for q in qs if q <= 5)
        if c == 0:
            continue
        Y[s, list(H)] = 1
        W[s, list(H)] += c
        bills[s] += c
    held = [t for t, mm in zip(case.types, m, strict=True) if mm]
    act_c, act_k = Y.sum(1) > 0, Y.sum(0) > 0
    pos = [t for t in held if act_c[t[0]] and all(act_k[h] for h in t[1])]
    lean, ideo, align, dist = R.covariates(case, Y)
    L = R.local_matrices(case, Y, W, bills, align, dist)
    P = {}
    prof = {tau: R.fit_bm(case, Y, tau, align, dist)[2] for tau in R.TAU_GRID}
    tau_hat = max(prof, key=prof.get)
    P["BM"], _, _ = R.fit_bm(case, Y, tau_hat, align, dist)
    P["BS1"], _ = R.fit_bs(case, Y, align, dist, covs=True)
    P["LR"] = R.lr_probs(case, L)
    P["TERGM"] = np.loadtxt(f"{outdir}/forecast_P.csv", delimiter=",")

    def sc(s, H):
        Hl = sorted(H)
        out = {
            k: float(L[k][s, Hl].mean())
            for k in ("cofunding", "path3", "weighted_footprint", "popularity")
        }
        for k, Pm in P.items():
            out[k] = float(np.exp(np.log(np.clip(Pm[s, Hl], 1e-300, 1)).mean()))
        return out

    sets = {}
    for kind in ("random", "matched", "perturb"):
        neg = F.negatives(case, pos, Y, "MCAR", 1, kind, lean=lean)
        sets[kind] = [
            (sc(*p), sc(*q), {"committee": int(p[0])})
            for p, q in zip(pos, neg, strict=True)
            if q is not None
        ]
    res = {
        "info": {
            "cycle": int(cycle),
            "target_types": int(m.sum()),
            "evaluated": len(pos),
            "tau_hat": tau_hat,
        },
        **sets,
    }
    pickle.dump(res, open(f"{outdir}/scores.pkl", "wb"))
    print(res["info"], flush=True)


def fitpy(fec_dir, dime, cycle, outdir, R=100):
    """Bootstrapped MPLE of the lagged TERGM (tergm_py, equivalent to btergm for these terms)."""
    import csv

    import tergm_py

    case = F.build_case(fec_dir, dime, int(cycle))
    A = nets(case, batch_quarters(case))
    X0 = exo(case)
    names = None
    blocks = []
    for t in range(1, 6):
        L = lagged(case, A[:t].sum(0), A[t - 1])
        keys = list(L) + list(X0)
        names = ["edges", *keys]
        cols = (
            [np.ones(case.C * case.K, np.float32)]
            + [np.asarray(L[k], np.float32).ravel() for k in L]
            + [np.asarray(X0[k], np.float32).ravel() for k in X0]
        )
        blocks.append((np.stack(cols, 1), (A[t] > 0).ravel().astype(float)))
    est, lo, hi = tergm_py.fit(blocks, R=int(R))
    with open(f"{outdir}/tergm_coef.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["term", "estimate", "2.5%", "97.5%"])
        for row in zip(names, est, lo, hi, strict=True):
            wr.writerow([row[0], *[f"{v:.6g}" for v in row[1:]]])
    L = lagged(case, A[:6].sum(0), A[5])
    eta = (
        est[0]
        + sum(est[1 + j] * L[k] for j, k in enumerate(L))
        + sum(est[1 + len(L) + j] * X0[k] for j, k in enumerate(X0))
    )
    np.savetxt(f"{outdir}/forecast_P.csv", 1 / (1 + np.exp(-eta)), delimiter=",", fmt="%.6g")
    print(cycle, dict(zip(names, np.round(est, 3), strict=True)), flush=True)


if __name__ == "__main__":
    stage = sys.argv[1]
    {"export": export, "score": score, "fitpy": fitpy}[stage](*sys.argv[2:6])
