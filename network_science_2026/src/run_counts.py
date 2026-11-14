# ruff: noqa: E501
"""Counts versus binary: pairwise models with the log number of shared records as an edge covariate.

For every mask of run_v3, adds log(1 + s_ij), where s_ij is the number of training records in
which i and j both participate (the co-membership counts used by the closure term of HM), as
an edge covariate to M5 (MPLE at the decay selected in run_v3), S1 (exact MLE), UM (MPLE with
profile-selected decay) and as a feature of the logistic regression; scores the random,
party-matched and head-perturbation pairs of run_v3.

Usage: python run_counts.py CASE V3_DIR OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import benchmark
import ergm
import numpy as np
import p1
import runlib
import um
from run_v2 import matched_negatives
from run_v3 import MLE_MODELS, fit_mple, overlap_matrix, perturb_negatives
from run_v4 import supervised_probs


def run_split(case, mech, rep, allowed, tau_hat):
    m, _ = case.mask(mech, rep)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    bills = np.zeros(n)
    events = []
    Bm = []
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            bills[s] += c
            events.append({s, *H})
            row = np.zeros(n)
            row[[s, *H]] = np.sqrt(c)
            Bm.append(row)
    Bm = np.array(Bm)
    Scount = Bm.T @ Bm
    np.fill_diagonal(Scount, 0)
    cov = dict(case.cov, logcount=np.log1p(Scount))
    P = {}
    ergm.DECAY = tau_hat
    terms = ergm.LADDER["M5"] + ["edgecov_logcount"]
    th, _ = fit_mple(Y, terms, cov)
    P["M5c"], _ = ergm.conditional_probs(Y, terms, th, cov)
    ergm.DECAY = 0.5
    terms = MLE_MODELS["S1"] + ["edgecov_logcount"]
    th, _ = p1.fit(Y, terms, cov, allowed=allowed)
    P["S1c"], _ = ergm.conditional_probs(Y, terms, th, cov)
    umod = um.fit(events, n, cov, terms=um.TERMS + ["logcount"])
    P["LRc"] = _lr_counts(Y, cov, bills, allowed)
    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]

    def score(s, H):
        Hl = sorted(H)
        out = {k: float(np.exp(np.log(np.clip(M[s, Hl], 1e-300, 1)).mean())) for k, M in P.items()}
        out["UMc"] = um.score(umod, {s, *H})
        out["weighted_footprint"] = float(W[s, Hl].mean())
        return out

    negs, _ = case.random_negatives(pos, R, mech, rep)
    mneg, _ = matched_negatives(case, pos, R, mech, rep)
    pneg = perturb_negatives(case, pos, R, mech, rep)
    sets = {"random": [], "matched": [], "perturb": []}
    for k, (s, H) in enumerate(pos):
        sp = score(s, H)
        for name, q in [("random", negs[k]), ("matched", mneg[k]), ("perturb", pneg[k])]:
            if q is not None:
                sets[name].append((sp, score(*q)))
    return {"um_tau": umod["tau"], "logcount_coef": {"M5c": float(th[-1]) if False else None}, **sets}


def _lr_counts(Y, cov, bills, allowed):
    import run_v4

    feats0 = run_v4.FEATS
    orig = run_v4.benchmark.local_matrices

    def lm(Y_, cov_):
        L = orig(Y_, cov_)
        L["logcount"] = cov_["logcount"]
        return L

    run_v4.benchmark.local_matrices = lm
    run_v4.FEATS = [*feats0, "logcount"]
    try:
        return supervised_probs(Y, cov, bills, allowed)
    finally:
        run_v4.FEATS = feats0
        run_v4.benchmark.local_matrices = orig


def main(name, v3dir, outdir, reps=30):
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
            r = run_split(case, mech, rep, allowed, old["info"]["tau_hat"])
            for k in ("random", "matched", "perturb"):
                a = [p[i]["weighted_footprint"] for p in r[k] for i in (0, 1)]
                b = [p[i]["weighted_footprint"] for p in old[k] for i in (0, 1)]
                assert len(a) == len(b) and np.allclose(a, b), (name, mech, rep, k)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 30)
