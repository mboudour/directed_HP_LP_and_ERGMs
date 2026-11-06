# ruff: noqa: E501
"""Valued ERGM of the weighted undirected 2-section (run_vm.py) against HM, UM, M5 and the
co-participation heuristic: concordance and sponsor-bootstrap contrasts.

Usage: python summary_vm.py RESULTS_DIR OUT_JSON
"""

import json
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot, win

CASES = ["s118", "s117", "s116", "h118"]
KEYS = ["VM", "UM", "HM", "M5", "coparticipation"]
CONTRASTS = [("VM", "UM"), ("HM", "VM"), ("VM", "M5"), ("coparticipation", "VM")]


def merged(res, case, mech, rep):
    f = f"{mech}_{rep:02d}.pkl"
    parts = [pickle.load(open(f"{res}/{d}_{case}/{f}", "rb")) for d in ("v3", "hm", "um", "vm", "coal")]
    out = {}
    for s in ("random", "matched", "perturb"):
        rows = []
        for i, x in enumerate(parts[0][s]):
            p, q = dict(x[0]), dict(x[1])
            for e in parts[1:]:
                p.update(e[s][i][0])
                q.update(e[s][i][1])
            rows.append((p, q, x[2]["sponsor"]))
        out[s] = rows
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
                M[s + "_contrasts"] = {f"{x} - {y}": [float(np.mean([(win(r[s], x) - win(r[s], y)).mean() for r in rs])), *cluster_boot([win(r[s], x) - win(r[s], y) for r in rs], spon)] for x, y in CONTRASTS}
            M["theta"] = {k: float(np.mean([pickle.load(open(f"{res}/vm_{case}/{mech}_{r:02d}.pkl", "rb"))["theta"][k] for r in range(1, reps + 1)])) for k in ("party", "state", "ideology")}
            S[case][mech] = M
            print(case, mech, {s: {k: round(v, 3) for k, v in M[s].items()} for s in ("random", "matched", "perturb")}, flush=True)
            print("   ", {s: {k: [round(x, 3) for x in v] for k, v in M[s + "_contrasts"].items()} for s in ("random", "matched", "perturb")}, flush=True)
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
