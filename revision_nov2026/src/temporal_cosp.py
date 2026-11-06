# ruff: noqa: E501
"""Temporal forecasting benchmark for co-sponsorship.

The bills of a Congress are divided into quarters by introduction date (eight quarters).
Bills of quarters 0-5 are the training record; bills of quarters 6-7 (the last six months)
are the target. Two stages:

  export  writes, for btergm, the quarterly directed networks of quarters 1-5 and, for each,
          lagged edge covariates computed from the earlier quarters (memory: arc in the
          previous quarter; delayed reciprocity; log history count of the arc; log lagged
          out-degree of the sender and in-degree of the receiver; log lagged two-paths),
          plus party and state matching and ideological distance; and the same covariates
          for the forecast window, computed from quarters 0-5.
  score   reads the btergm forecast probabilities, fits the static models (M5, S1, HM, UM)
          and computes co-participation and directed Adamic--Adar on the training record,
          builds the random, party-matched and head-perturbation candidate sets and the
          role-assignment sets for the target bills (same rules as the mask benchmark), and
          stores all scores.

Usage: python temporal_cosp.py export CASE OUTDIR
       python temporal_cosp.py fitpy CASE OUTDIR    (TERGM in Python, instead of tergm_forecast.R)
       (environment TARGET_START=7 forecasts the last quarter instead of the last six months)
       python temporal_cosp.py score CASE OUTDIR
"""

import datetime as dt
import os
import pickle
import sys

import actors
import benchmark
import ergm
import hm
import numpy as np
import p1
import runlib
import um
from run_v2 import matched_negatives
from run_v3 import MLE_MODELS, TAU_GRID, fit_mple, overlap_matrix, perturb_negatives

T0 = int(os.environ.get("TARGET_START", "6"))  # first target quarter; 6 = last six months, 7 = last quarter
TRAIN_Q, TARGET_Q = range(0, T0), tuple(range(T0, 8))


def quarters(case):
    t0 = dt.date.fromisoformat(actors.CONGRESS_DATES[case.congress][0])
    return np.array([min((d - t0).days for d in case.type_dates[t]) // 91 for t in case.types])


def nets(case, q):
    n = case.n
    A = np.zeros((8, n, n))
    for (s, H), c, qq in zip(case.types, case.counts, q, strict=True):
        A[min(qq, 7), s, list(H)] += c
    return A


def lagged(A_hist, n):
    """Edge covariates from a weighted history matrix (sum of earlier quarters) and the last quarter."""
    H = A_hist
    B = (H > 0).astype(float)
    out = np.log1p(B.sum(1))[:, None] * np.ones((1, n))
    inn = np.ones((n, 1)) * np.log1p(B.sum(0))[None, :]
    two = np.log1p(B @ B)
    np.fill_diagonal(two, 0)
    return {"history": np.log1p(H), "hist_rev": np.log1p(H.T), "out_lag": out, "in_lag": inn, "twopath_lag": two}


def exo(case):
    cov = case.cov
    return {
        "party": (cov["party"][:, None] == cov["party"][None, :]).astype(float),
        "state": (cov["state"][:, None] == cov["state"][None, :]).astype(float),
        "ideology": np.abs(cov["nominate"][:, None] - cov["nominate"][None, :]),
    }


def export(name, outdir):
    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    q = quarters(case)
    A = nets(case, q)
    n = case.n
    X = exo(case)
    for k, M in X.items():
        np.savetxt(f"{outdir}/exo_{k}.csv", M, delimiter=",", fmt="%.6g")
    for t in range(1, T0):
        np.savetxt(f"{outdir}/net_{t}.csv", (A[t] > 0).astype(int), delimiter=",", fmt="%d")
        L = lagged(A[:t].sum(0), n)
        L["memory"] = (A[t - 1] > 0).astype(float)
        L["delrecip"] = (A[t - 1].T > 0).astype(float)
        for k, M in L.items():
            np.savetxt(f"{outdir}/lag_{t}_{k}.csv", M, delimiter=",", fmt="%.6g")
    L = lagged(A[:T0].sum(0), n)
    L["memory"] = (A[T0 - 1] > 0).astype(float)
    L["delrecip"] = (A[T0 - 1].T > 0).astype(float)
    for k, M in L.items():
        np.savetxt(f"{outdir}/lag_target_{k}.csv", M, delimiter=",", fmt="%.6g")
    tgt = A[T0:].sum(0) > 0
    np.savetxt(f"{outdir}/net_target.csv", tgt.astype(int), delimiter=",", fmt="%d")
    pickle.dump({"quarters": q.tolist(), "n": n}, open(f"{outdir}/meta.pkl", "wb"))
    print(name, "train bills", int(np.isin(q, TRAIN_Q).sum()), "target bills", int((q >= T0).sum()), flush=True)


def score(name, outdir):
    case = runlib.make_case(name)
    q = quarters(case)
    m = q >= T0
    case.mask = lambda mech, rep, _m=m: (_m, 0)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    bills = np.zeros(n)
    events, weights = [], []
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=True):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            bills[s] += c
            events.append({s, *H})
            weights.append(c)
    allowed = overlap_matrix(case)
    cov = case.cov
    P = {}
    prof = {}
    for tau in TAU_GRID:
        ergm.DECAY = tau
        prof[tau] = fit_mple(Y, ergm.LADDER["M5"], cov)[1]
    tau_hat = max(prof, key=prof.get)
    ergm.DECAY = tau_hat
    th, _ = fit_mple(Y, ergm.LADDER["M5"], cov)
    P["M5"], _ = ergm.conditional_probs(Y, ergm.LADDER["M5"], th, cov)
    ergm.DECAY = 0.5
    th, _ = p1.fit(Y, MLE_MODELS["S1"], cov, allowed=allowed)
    P["S1"], _ = ergm.conditional_probs(Y, MLE_MODELS["S1"], th, cov)
    P["TERGM"] = np.loadtxt(f"{outdir}/forecast_P.csv", delimiter=",")
    hmod = hm.fit(events, weights, n, cov, hm.TERMS_HM)
    umod = um.fit(events, n, cov)
    B = np.zeros((len(events), n))
    for e, Pp in enumerate(events):
        B[e, list(Pp)] = np.sqrt(weights[e])
    Cp = B.T @ B
    Lm = benchmark.local_matrices(Y, cov)

    def sc(s, H):
        Hl = sorted(H)
        Pp = sorted({s, *H})
        iu = np.triu_indices(len(Pp), 1)
        out = {k: float(np.exp(np.log(np.clip(M[s, Hl], 1e-300, 1)).mean())) for k, M in P.items()}
        out["HM"] = hm.score(hmod, Pp)
        out["UM"] = um.score(umod, Pp)
        out["coparticipation"] = float(Cp[np.ix_(Pp, Pp)][iu].mean())
        out["aa_total"] = float(Lm["aa_total"][s, Hl].mean())
        out["weighted_footprint"] = float(W[s, Hl].mean())
        out["sponsor_bills"] = float(bills[s])
        return out

    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=True) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
    negs, _ = case.random_negatives(pos, R, "MCAR", 1)
    mneg, _ = matched_negatives(case, pos, R, "MCAR", 1)
    pneg = perturb_negatives(case, pos, R, "MCAR", 1)
    sets = {"random": [], "matched": [], "perturb": []}
    role = []
    for k, (s, H) in enumerate(pos):
        sp = sc(s, H)
        for nm, qq in (("random", negs[k]), ("matched", mneg[k]), ("perturb", pneg[k])):
            if qq is not None:
                sets[nm].append((sp, sc(*qq), {"sponsor": int(s), "other": sum(int(cov["caucus"][h] != cov["caucus"][s]) for h in H)}))
        Pset = sorted(H | {s})
        role.append(([sc(x, frozenset(Pset) - {x}) for x in Pset], Pset.index(s), int(s)))
    res = {"info": {"case": name, "train": int((~m).sum()), "target": int(m.sum()), "evaluated": len(pos), "tau_hat": tau_hat}, **sets, "role": role}
    pickle.dump(res, open(f"{outdir}/scores.pkl", "wb"))
    print(name, res["info"], flush=True)


def fitpy(name, outdir, R=100):
    """Bootstrapped MPLE of the lagged TERGM with tergm_py (equivalent to btergm for these terms),
    from the files written by export; writes forecast_P.csv and tergm_coef.csv."""
    import csv
    import glob

    import tergm_py

    rd = lambda f: np.loadtxt(f"{outdir}/{f}", delimiter=",")
    lagk = sorted(os.path.basename(f)[6:-4] for f in glob.glob(f"{outdir}/lag_1_*.csv"))
    exok = sorted(os.path.basename(f)[4:-4] for f in glob.glob(f"{outdir}/exo_*.csv"))
    E = {k: rd(f"exo_{k}.csv") for k in exok}
    n = E[exok[0]].shape[0]
    off = ~np.eye(n, dtype=bool)
    names = ["edges", *lagk, *exok]
    blocks = []
    for t in range(1, T0):
        cols = [np.ones(off.sum(), np.float32)] + [rd(f"lag_{t}_{k}.csv")[off].astype(np.float32) for k in lagk] + [E[k][off].astype(np.float32) for k in exok]
        blocks.append((np.stack(cols, 1), rd(f"net_{t}.csv")[off].astype(float)))
    est, lo, hi = tergm_py.fit(blocks, R=int(R))
    with open(f"{outdir}/tergm_coef.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["term", "estimate", "2.5%", "97.5%"])
        for row in zip(names, est, lo, hi, strict=True):
            wr.writerow([row[0], *[f"{v:.6g}" for v in row[1:]]])
    eta = est[0] + sum(est[1 + j] * rd(f"lag_target_{k}.csv") for j, k in enumerate(lagk)) + sum(est[1 + len(lagk) + j] * E[k] for j, k in enumerate(exok))
    np.savetxt(f"{outdir}/forecast_P.csv", 1 / (1 + np.exp(-eta)), delimiter=",", fmt="%.6g")
    print(name, dict(zip(names, np.round(est, 3), strict=True)), flush=True)


if __name__ == "__main__":
    stage, name, outdir = sys.argv[1:4]
    {"export": export, "score": score, "fitpy": fitpy}[stage](name, outdir)
