"""Exact joint footprint scores L_J (log scale) for M4c and M5 on the random
and sponsor-substitution panels. Candidates are regenerated deterministically
from the frozen masks; fitted coefficients are read from the main run."""

import os
import pickle
import sys
import time

import benchmark
import ergm
import numpy as np
import runlib


def main(name, resdir, outdir, mech, reps):
    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    for rep in reps:
        f = f"{outdir}/{mech}_{rep:02d}.pkl"
        if os.path.exists(f):
            continue
        t = time.time()
        r = pickle.load(open(f"{resdir}/{mech}_{rep:02d}.pkl", "rb"))
        m, _ = case.mask(mech, rep)
        Y = np.zeros((case.n, case.n), np.int8)
        for (s, H), mm in zip(case.types, m, strict=False):
            if not mm:
                Y[s, list(H)] = 1
        R = benchmark.reach2(Y)
        held = [t_ for t_, mm in zip(case.types, m, strict=False) if mm]
        pos = [t_ for t_ in held if R[np.ix_(list(t_[1] | {t_[0]}), list(t_[1] | {t_[0]}))].all()]
        negs, _ = case.random_negatives(pos, R, mech, rep)
        rand = [(p, q) for p, q in zip(pos, negs, strict=False) if q is not None]
        subs = benchmark.substitution_pairs(case, pos, R, mech, rep)
        assert len(rand) == len(r["random"]) and len(subs) == len(r["sub"])
        out = {}
        for model in ["M4c", "M5"]:
            th = np.array(r["theta"][model])
            terms = ergm.LADDER[model]

            def lj(c, Y=Y, terms=terms, th=th):
                return benchmark.joint_footprint_logprob(Y, c[0], sorted(c[1]), terms, th, case.cov)

            out[model] = {
                "random": [(lj(p), lj(q)) for p, q in rand],
                "sub": [(lj(p), lj(q)) for p, q in subs],
            }
        pickle.dump(out, open(f, "wb"))
        print(name, mech, rep, round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    name, resdir, outdir, mech, a, b = sys.argv[1:7]
    main(name, resdir, outdir, mech, range(int(a), int(b) + 1))
