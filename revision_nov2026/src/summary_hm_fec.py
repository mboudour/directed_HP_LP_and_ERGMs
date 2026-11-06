# ruff: noqa: E501
"""Two-mode ERGM for contributions (run_hm_fec.py) against the bipartite ERGMs, the logistic
regression and co-funding similarity: concordance and committee-bootstrap contrasts.

Usage: python summary_hm_fec.py RESULTS_DIR OUT_JSON
"""

import json
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot, win

KEYS = ["HM", "HM0", "BM", "BS1", "LR", "cofunding"]
CONTRASTS = [("HM", "BM"), ("HM", "BS1"), ("HM", "HM0"), ("LR", "HM"), ("cofunding", "HM")]


def main(res, out, reps=20):
    S = {}
    for cyc in ("fec24", "fec22"):
        S[cyc] = {}
        for mech in ("MCAR", "MNAR-out"):
            rs = []
            for r in range(1, reps + 1):
                a = pickle.load(open(f"{res}/{cyc}/{mech}_{r:02d}.pkl", "rb"))
                h = pickle.load(open(f"{res}/hmfec_{cyc}/{mech}_{r:02d}.pkl", "rb"))
                rs.append({s: [({**x[0], **y[0]}, {**x[1], **y[1]}, x[2]["committee"]) for x, y in zip(a[s], h[s], strict=True)] for s in ("random", "matched", "perturb")} | {"theta": h["theta"]["HM"]})
            M = {}
            for s in ("random", "matched", "perturb"):
                M[s] = {k: float(np.mean([win(r[s], k).mean() for r in rs])) for k in KEYS}
                g = [np.array([p[2] for p in r[s]]) for r in rs]
                M[s + "_contrasts"] = {f"{x} - {y}": [float(np.mean([(win(r[s], x) - win(r[s], y)).mean() for r in rs])), *cluster_boot([win(r[s], x) - win(r[s], y) for r in rs], g)] for x, y in CONTRASTS}
            M["theta"] = {k: float(np.mean([r["theta"][k] for r in rs])) for k in rs[0]["theta"]}
            S[cyc][mech] = M
            print(cyc, mech, {s: {k: round(v, 3) for k, v in M[s].items()} for s in ("random", "matched", "perturb")})
            print("   ", {s: {k: [round(x, 3) for x in v] for k, v in M[s + "_contrasts"].items()} for s in ("random", "matched", "perturb")})
            print("   ", {k: round(v, 3) for k, v in M["theta"].items()})
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
