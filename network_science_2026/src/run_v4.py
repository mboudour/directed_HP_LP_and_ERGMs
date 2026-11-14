# ruff: noqa: E501
"""Fourth run: ablation of the degree-term family at the selected decay and a supervised baseline.

For each mask this script reuses the selected decay of run_v3 (info["tau_hat"]) and fits by MPLE
  * M2, M3, M4, M4c, M5 at the selected decay (keys with no suffix);
  * M5 with the degree terms at decay 0.5 and the shared-partner terms at the selected decay
    (key M5_deg05), and the reverse (key M5_esp05);
and a supervised baseline LR: a logistic regression of the arcs of the training 2-section on
standardized dyadic features (directed common neighbours and Adamic--Adar components,
reverse arc, out- and in-degrees and their product computed without the dyad itself,
initiator bill count, party and state matching, ideological distance, majority caucus and
seniority of the initiator). Candidates: random, head perturbation, substitution and role
assignment, regenerated deterministically as in run_v3.

Usage: python run_v4.py CASE OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import benchmark
import ergm
import numpy as np
import runlib
from run_v3 import fit_mple, perturb_negatives
from sklearn.linear_model import LogisticRegression

MODELS = ["M2", "M3", "M4", "M4c", "M5"]
FEATS = ["cn_oi", "cn_oo", "cn_ii", "aa_oi", "aa_oo", "aa_ii", "reverse"]


def supervised_probs(Y, cov, bills, allowed):
    n = Y.shape[0]
    L = benchmark.local_matrices(Y, cov)
    A = Y.astype(float)
    dout = A.sum(1)[:, None] - A
    din = A.sum(0)[None, :] - A
    X = [L[k] for k in FEATS]
    X += [dout, din, dout * din, np.repeat(np.log1p(bills)[:, None], n, 1)]
    X += [
        (cov["party"][:, None] == cov["party"][None, :]).astype(float),
        (cov["state"][:, None] == cov["state"][None, :]).astype(float),
        np.abs(cov["nominate"][:, None] - cov["nominate"][None, :]),
        np.repeat(cov["majority"][:, None].astype(float), n, 1),
        np.repeat(cov["seniority"][:, None].astype(float), n, 1),
    ]
    F = np.stack(X, -1)
    mask = allowed & ~np.eye(n, dtype=bool)
    Xtr = F[mask]
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-12
    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit((Xtr - mu) / sd, A[mask])
    P = clf.predict_proba((F.reshape(-1, F.shape[-1]) - mu) / sd)[:, 1].reshape(n, n)
    return P


def run_split(case, mech, rep, allowed, v3dir):
    r3 = pickle.load(open(f"{v3dir}/{mech}_{rep:02d}.pkl", "rb"))
    tau = r3["info"]["tau_hat"]
    m, _ = case.mask(mech, rep)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    bills = np.zeros(n)
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            bills[s] += c
    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
    cov = case.cov
    P, theta = {}, {}
    variants = [(k, tau, None) for k in MODELS] + [("M5_deg05", tau, 0.5), ("M5_esp05", 0.5, tau)]
    for name, t_esp, t_deg in variants:
        ergm.DECAY, ergm.DECAY_DEG = t_esp, t_deg
        terms = ergm.LADDER[name.split("_")[0]]
        th, _ = fit_mple(Y, terms, cov)
        theta[name] = dict(zip(ergm.expand_terms(terms, n), th.tolist(), strict=False))
        P[name], _ = ergm.conditional_probs(Y, terms, th, cov)
    ergm.DECAY, ergm.DECAY_DEG = 0.5, None
    P["LR"] = supervised_probs(Y, cov, bills, allowed)

    def score(s, H):
        Hl = sorted(H)
        return {
            k: float(np.exp(np.log(np.clip(Pm[s, Hl], 1e-300, 1)).mean())) for k, Pm in P.items()
        }

    negs, _ = case.random_negatives(pos, R, mech, rep)
    pneg = perturb_negatives(case, pos, R, mech, rep)
    subs = dict(benchmark.substitution_pairs(case, pos, R, mech, rep))
    sets = {"random": [], "perturb": [], "sub": []}
    role = []
    for k, (s, H) in enumerate(pos):
        sp_ = score(s, H)
        mt = {"size": len(H), "sponsor": int(s)}
        for name, q in [("random", negs[k]), ("perturb", pneg[k]), ("sub", subs.get((s, H)))]:
            if q is not None:
                sets[name].append((sp_, score(*q), mt))
        Pset = sorted(H | {s})
        role.append(([score(x, frozenset(Pset) - {x}) for x in Pset], Pset.index(s), mt))
    return {
        "info": {"mech": mech, "replicate": rep, "tau_hat": tau},
        "theta": theta,
        **sets,
        "role": role,
    }


def main(name, outdir, reps=30):
    from run_v3 import overlap_matrix

    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    allowed = overlap_matrix(case)
    v3dir = outdir.replace("v4_", "v3_")
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = run_split(case, mech, rep, allowed, v3dir)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30)
