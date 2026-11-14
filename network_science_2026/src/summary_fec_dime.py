# ruff: noqa: E501
"""Compare the benchmark with committee ideology from DIME contributor scores against the
main specification on the same masks.

Usage: python summary_fec_dime.py RESULTS_DIR COVERAGE_JSON OUT_JSON
"""

import glob
import json
import os
import pickle
import sys

import numpy as np
from summary_v3 import win

KEYS = ["BS1", "BM", "LR", "proximity", "cofunding"]


def main(resdir, cov_json, out):
    S = {"coverage": json.load(open(cov_json))}
    for key in ("fec24", "fec22"):
        o = {}
        for mech in ("MCAR", "MNAR-out"):
            fs = sorted(glob.glob(f"{resdir}/{key}_dime/{mech}_*.pkl"))
            base = [pickle.load(open(f"{resdir}/{key}/{os.path.basename(f)}", "rb")) for f in fs]
            alt = [pickle.load(open(f, "rb")) for f in fs]
            M = {"masks": len(fs)}
            for s in ("random", "matched", "perturb"):
                M[s] = {
                    k: {
                        "main": float(np.mean([win(r[s], k).mean() for r in base])),
                        "dime": float(np.mean([win(r[s], k).mean() for r in alt])),
                    }
                    for k in KEYS
                }
            M["theta_BS1"] = {
                "main": np.mean([r["theta"]["BS1"] for r in base], 0).tolist(),
                "dime": np.mean([r["theta"]["BS1"] for r in alt], 0).tolist(),
            }
            o[mech] = M
        S[key] = o
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
