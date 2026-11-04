# ruff: noqa: E501
"""Coalition-aware and item-based scores for the co-sponsorship benchmark.

For every mask of run_v3, rebuilds the training record and the random, party-matched and
head-perturbation candidate sets (same seeds and constraints), and scores each candidate with
  * co-participation: mean, over all pairs of participants of the candidate hyperarc, of the
    number of training records in which both participate (a score of the coalition as a whole,
    not of its arcs);
  * co-support similarity: the item-based collaborative filter used for contributions, i.e. the
    mean cosine similarity (common initiators over the geometric mean of in-degrees) between the
    supporter and the supporters of the initiator, averaged over the footprint;
  * weighted footprint, recomputed to check that the pairs align with the stored run.

Usage: python run_coal.py CASE V3_DIR OUTDIR [REPS]
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


def item_similarity(A):
    T = A.T @ A
    dk = np.maximum(A.sum(0), 1)
    Sim = T / np.sqrt(dk[:, None] * dk[None, :])
    np.fill_diagonal(Sim, 0)
    return (A @ Sim) / np.maximum(A.sum(1), 1)[:, None]


def run_split(case, mech, rep):
    m, _ = case.mask(mech, rep)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    B = []
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            row = np.zeros(n)
            row[[s, *H]] = 1
            B.append(row * np.sqrt(c))
    B = np.array(B)
    Cp = B.T @ B
    CF = item_similarity(Y.astype(float))
    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]

    def score(s, H):
        Hl = sorted(H)
        P = [s, *Hl]
        iu = np.triu_indices(len(P), 1)
        return {
            "coparticipation": float(Cp[np.ix_(P, P)][iu].mean()),
            "cosupport": float(CF[s, Hl].mean()),
            "weighted_footprint": float(W[s, Hl].mean()),
        }

    negs, _ = case.random_negatives(pos, R, mech, rep)
    mneg, _ = matched_negatives(case, pos, R, mech, rep)
    pneg = perturb_negatives(case, pos, R, mech, rep)
    sets = {"random": [], "matched": [], "perturb": []}
    for k, (s, H) in enumerate(pos):
        sp = score(s, H)
        for name, q in [("random", negs[k]), ("matched", mneg[k]), ("perturb", pneg[k])]:
            if q is not None:
                sets[name].append((sp, score(*q)))
    return sets


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
            for k in r:
                a = [p[0]["weighted_footprint"] for p in r[k]] + [
                    p[1]["weighted_footprint"] for p in r[k]
                ]
                b = [p[0]["weighted_footprint"] for p in old[k]] + [
                    p[1]["weighted_footprint"] for p in old[k]
                ]
                assert len(a) == len(b) and np.allclose(a, b), (name, mech, rep, k)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 30)
