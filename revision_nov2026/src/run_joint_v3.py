# ruff: noqa: E501
"""Exact joint footprint scores L_J for M4c and M5 with the selected decay (third run).

Candidates (random and head-perturbation sets) are regenerated deterministically from
the frozen masks; coefficients and the decay are read from the run_v3 pickles. Writes
per-mask within-pair concordance of L_J, of L_J per arc and of L_1g.

Usage: python run_joint_v3.py CASE V3_DIR OUT_JSON MECH FIRST LAST
"""

import json
import pickle
import sys

import benchmark
import ergm
import numpy as np
import runlib
from run_v3 import perturb_negatives


def conc(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(((a > b) + 0.5 * (a == b)).mean())


def main(name, v3dir, out, mech, first, last):
    case = runlib.make_case(name)
    res = {}
    for rep in range(first, last + 1):
        r = pickle.load(open(f"{v3dir}/{mech}_{rep:02d}.pkl", "rb"))
        ergm.DECAY = r["info"]["tau_hat"]
        m, _ = case.mask(mech, rep)
        Y = np.zeros((case.n, case.n), np.int8)
        for (s, H), mm in zip(case.types, m, strict=False):
            if not mm:
                Y[s, list(H)] = 1
        R = benchmark.reach2(Y)
        held = [t for t, mm in zip(case.types, m, strict=False) if mm]
        pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
        negs, _ = case.random_negatives(pos, R, mech, rep)
        pneg = perturb_negatives(case, pos, R, mech, rep)
        sets = {
            "random": [(p, q) for p, q in zip(pos, negs, strict=False) if q is not None],
            "perturb": [(p, q) for p, q in zip(pos, pneg, strict=False) if q is not None],
        }
        out_r = {}
        for model in ["M4c", "M5"]:
            terms = ergm.LADDER[model]
            th = np.array([r["theta"][model][t] for t in terms])
            for sname, pairs in sets.items():
                lj = [
                    (
                        benchmark.joint_footprint_logprob(
                            Y, p[0], sorted(p[1]), terms, th, case.cov
                        ),
                        benchmark.joint_footprint_logprob(
                            Y, q[0], sorted(q[1]), terms, th, case.cov
                        ),
                    )
                    for p, q in pairs
                ]
                k = np.array([len(p[1]) for p, _ in pairs])
                a, b = np.array([x for x, _ in lj]), np.array([y for _, y in lj])
                l1g = [(x[0][model], x[1][model]) for x in r[sname]]
                out_r[f"{model}|{sname}"] = {
                    "LJ": conc(a, b),
                    "LJ_per_arc": conc(a / k, b / k),
                    "L1g": conc([x for x, _ in l1g], [y for _, y in l1g]),
                }
        res[rep] = out_r
        print(name, mech, rep, out_r, flush=True)
        json.dump(res, open(out, "w"), indent=1)
    ergm.DECAY = 0.5


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4], int(a[5]), int(a[6]))
