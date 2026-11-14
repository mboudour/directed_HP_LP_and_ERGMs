# ruff: noqa: E501
"""HM, HM0 and the directed ERGMs trained on all bills (runs <case>uncap of run_v3.py and run_hm.py).

Concordance on the random, party-matched and head-perturbation sets, with sponsor-bootstrap
intervals for paired contrasts.

Usage: python summary_hm_uncap.py RESULTS_DIR OUT_JSON
"""

import json
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot, win

CASES = ["s118", "s117", "s116", "h118"]
KEYS = ["HM", "HM0", "M5", "S1", "weighted_footprint"]
CONTRASTS = [("HM", "M5"), ("HM", "S1"), ("HM", "weighted_footprint"), ("HM", "HM0")]


def merged(res, case, mech, rep):
    f = f"{mech}_{rep:02d}.pkl"
    a = pickle.load(open(f"{res}/v3_{case}uncap/{f}", "rb"))
    h = pickle.load(open(f"{res}/hm_{case}uncap/{f}", "rb"))
    out = {}
    for s in ("random", "matched", "perturb"):
        out[s] = [({**x[0], **y[0]}, {**x[1], **y[1]}, x[2]["sponsor"]) for x, y in zip(a[s], h[s], strict=True)]
    return out


def main(res, out, reps=30):
    S = {}
    for case in CASES:
        S[case] = {}
        for mech in ("MCAR", "MNAR-out"):
            rs = [merged(res, case, mech, r) for r in range(1, reps + 1)]
            M = {}
            for s in ("random", "matched", "perturb"):
                M[s] = {k: float(np.mean([win(r[s], k).mean() for r in rs])) for k in KEYS}
                spon = [np.array([p[2] for p in r[s]]) for r in rs]
                M[s + "_contrasts"] = {}
                for x, y in CONTRASTS:
                    vec = [win(r[s], x) - win(r[s], y) for r in rs]
                    M[s + "_contrasts"][f"{x} - {y}"] = [float(np.mean([v.mean() for v in vec])), *cluster_boot(vec, spon)]
            S[case][mech] = M
            print(case, mech, {s: {k: round(v, 3) for k, v in M[s].items()} for s in ("random", "matched", "perturb")}, flush=True)
            print("   ", {s: {k: [round(x, 3) for x in v] for k, v in M[s + "_contrasts"].items()} for s in ("random", "matched", "perturb")}, flush=True)
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
