# ruff: noqa: E501
"""Higher-order ERGM (two-mode incidence network) on the co-sponsorship benchmark.

For every mask of run_v3, fits HM and HM0 (hm.py) by MPLE to the training records and scores
the random, party-matched and head-perturbation pairs (same seeds and constraints as run_v3);
alignment with the stored pairs is checked through the weighted footprint.

Usage: python run_hm.py CASE V3_DIR OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import benchmark
import hm
import numpy as np
import runlib
from run_v2 import matched_negatives
from run_v3 import perturb_negatives


def run_split(case, mech, rep):
    m, _ = case.mask(mech, rep)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    events, weights = [], []
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            events.append({s, *H})
            weights.append(c)
    models = {
        name: hm.fit(events, weights, n, case.cov, terms)
        for name, terms in (("HM", hm.TERMS_HM), ("HM0", hm.TERMS_HM0))
    }
    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]

    def score(s, H):
        P = {s, *H}
        out = {k: hm.score(md, P) for k, md in models.items()}
        out["weighted_footprint"] = float(W[s, sorted(H)].mean())
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
    theta = {
        k: dict(zip(md["terms"], md["theta"].tolist(), strict=True)) for k, md in models.items()
    }
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
            print(
                name,
                mech,
                rep,
                round(time.time() - t, 1),
                {k: round(v, 3) for k, v in r["theta"]["HM"].items()},
                flush=True,
            )


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 30)
