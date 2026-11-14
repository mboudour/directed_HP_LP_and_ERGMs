# ruff: noqa: E501
"""Valued ERGM of the weighted undirected 2-section (VM) on the co-sponsorship benchmark.

The weighted undirected 2-section gives, for every pair of actors, the number s_ij of training bills
(with multiplicity) in which both participate. VM is the dyad-independent valued ERGM with a Poisson
reference measure (Krivitsky 2012) with terms for the sum of counts, actor sociality (one parameter
per actor, the valued analogue of degree), and the counts within the same party and state and
weighted by ideological distance. Its likelihood is that of a Poisson regression
  log E[s_ij] = theta_0 + alpha_i + alpha_j + theta_p 1[same party] + theta_s 1[same state] + theta_d |x_i - x_j|,
fitted here by Newton's method with a small ridge on the sociality parameters. A candidate is scored
by the geometric mean of the expected counts over all pairs of its participants. Pairs and masks are
those of run_v3.py (alignment checked through the weighted pair count).

Usage: python run_vm.py CASE V3_DIR OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import benchmark
import numpy as np
import runlib
from run_v2 import matched_negatives
from run_v3 import perturb_negatives


def fit_poisson(S, cov, ridge=1e-3, iters=100):
    n = S.shape[0]
    iu = np.triu_indices(n, 1)
    y = S[iu]
    same_p = (cov["party"][:, None] == cov["party"][None, :])[iu].astype(float)
    same_s = (cov["state"][:, None] == cov["state"][None, :])[iu].astype(float)
    dist = np.abs(cov["nominate"][:, None] - cov["nominate"][None, :])[iu]
    Xc = np.stack([np.ones_like(y), same_p, same_s, dist], 1)
    i, j = iu
    p = Xc.shape[1]
    th = np.zeros(p + n)
    th[0] = np.log(max(y.mean(), 1e-6))
    for _ in range(iters):
        eta = Xc @ th[:p] + th[p + i] + th[p + j]
        mu = np.exp(eta)
        r = y - mu
        g = np.concatenate([Xc.T @ r, np.bincount(i, r, n) + np.bincount(j, r, n)])
        g[p:] -= 2 * ridge * th[p:]
        # Hessian blocks
        Hcc = (Xc * mu[:, None]).T @ Xc
        Hca = np.zeros((p, n))
        for k in range(p):
            Hca[k] = np.bincount(i, Xc[:, k] * mu, n) + np.bincount(j, Xc[:, k] * mu, n)
        Haa = np.zeros((n, n))
        np.add.at(Haa, (i, j), mu)
        Haa = Haa + Haa.T
        Haa[np.diag_indices(n)] = np.bincount(i, mu, n) + np.bincount(j, mu, n) + 2 * ridge
        H = np.block([[Hcc, Hca], [Hca.T, Haa]])
        step = np.linalg.solve(H + 1e-9 * np.eye(p + n), g)
        th += step
        if np.max(np.abs(step)) < 1e-7:
            break
    L = np.full((n, n), -np.inf)
    eta = Xc @ th[:p] + th[p + i] + th[p + j]
    L[iu] = eta
    L[(j, i)] = eta
    return L, dict(zip(["edges", "party", "state", "ideology"], th[:p].tolist(), strict=True))


def run_split(case, mech, rep):
    m, _ = case.mask(mech, rep)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    rows = []
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            r = np.zeros(n)
            r[[s, *H]] = np.sqrt(c)
            rows.append(r)
    B = np.array(rows)
    S = B.T @ B
    np.fill_diagonal(S, 0)
    logmu, theta = fit_poisson(S, case.cov)

    def score(s, H):
        P = sorted({s, *H})
        iu = np.triu_indices(len(P), 1)
        return {"VM": float(np.exp(logmu[np.ix_(P, P)][iu].mean())), "weighted_footprint": float(W[s, sorted(H)].mean())}

    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
    negs, _ = case.random_negatives(pos, R, mech, rep)
    mneg, _ = matched_negatives(case, pos, R, mech, rep)
    pneg = perturb_negatives(case, pos, R, mech, rep)
    sets = {"random": [], "matched": [], "perturb": []}
    for k, (s, H) in enumerate(pos):
        sp = score(s, H)
        for name, q in [("random", negs[k]), ("matched", mneg[k]), ("perturb", pneg[k])]:
            if q is not None:
                sets[name].append((sp, score(*q)))
    return {"theta": theta, **sets}


def main(name, v3dir, outdir, reps=30):
    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = run_split(case, mech, rep)
            old = pickle.load(open(f"{v3dir}/{mech}_{rep:02d}.pkl", "rb"))
            for k in ("random", "matched", "perturb"):
                a = [p[i]["weighted_footprint"] for p in r[k] for i in (0, 1)]
                b = [p[i]["weighted_footprint"] for p in old[k] for i in (0, 1)]
                assert len(a) == len(b) and np.allclose(a, b), (name, mech, rep, k)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, round(time.time() - t, 1), {k: round(v, 3) for k, v in r["theta"].items()}, flush=True)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 30)
