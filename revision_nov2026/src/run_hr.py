# ruff: noqa: E501
"""Role-labelled higher-order ERGM (hr.py) on the role-assignment and substitution sets.

Per mask of run_v3: fit on the training records; for every evaluated withheld hyperarc,
the probability that each participant is the initiator (role-assignment sets, participants
in sorted order as in run_v3) and the substitution pair (same participants, the substitute
initiator). Alignment with the stored substitution pairs is checked through the weighted
footprint.

Usage: python run_hr.py CASE V3_DIR OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import benchmark
import hr
import numpy as np
import runlib


def run_split(case, mech, rep):
    m, _ = case.mask(mech, rep)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    recs, wts = [], []
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            recs.append((s, H))
            wts.append(c)
    model = hr.fit(recs, wts, n)
    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
    subs = dict(benchmark.substitution_pairs(case, pos, R, mech, rep))
    role, sub = [], []
    for s, H in pos:
        P = sorted(H | {s})
        p = hr.probs(model, P)
        role.append((p.tolist(), P.index(s)))
        q = subs.get((s, H))
        if q is not None:
            h = q[0]
            sub.append(
                (
                    {
                        "HR": float(p[P.index(s)]),
                        "weighted_footprint": float(W[s, sorted(H)].mean()),
                    },
                    {
                        "HR": float(p[P.index(h)]),
                        "weighted_footprint": float(W[h, sorted(q[1])].mean()),
                    },
                )
            )
    return {
        "theta": dict(zip(hr.TERMS, model["theta"].tolist(), strict=True)),
        "role": role,
        "sub": sub,
    }


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
            assert len(r["role"]) == len(old["role"]) and all(
                x[1] == y[1] for x, y in zip(r["role"], old["role"], strict=True)
            ), (name, mech, rep, "role")
            a = [p[i]["weighted_footprint"] for p in r["sub"] for i in (0, 1)]
            b = [p[i]["weighted_footprint"] for p in old["sub"] for i in (0, 1)]
            assert len(a) == len(b) and np.allclose(a, b), (name, mech, rep, "sub")
            pickle.dump(r, open(f, "wb"))
            print(
                name,
                mech,
                rep,
                round(time.time() - t, 1),
                {k: round(v, 3) for k, v in r["theta"].items()},
                flush=True,
            )


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 30)
