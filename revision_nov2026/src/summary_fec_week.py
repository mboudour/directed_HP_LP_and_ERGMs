# ruff: noqa: E501
"""Contribution benchmark with seven-day windows: concordance on the first ten masks, with the
main specification (one date) on the same mask numbers for reference.

Usage: python summary_fec_week.py RESULTS_DIR OUT_JSON
"""

import glob
import json
import os
import pickle
import sys

import numpy as np
from summary_v3 import win

KEYS = ["BS1", "BM", "LR", "cofunding", "path3", "weighted_footprint"]


def main(resdir, out):
    S = {}
    for key in ("fec24", "fec22"):
        o = {
            "accounting_week": pickle.load(open(f"{resdir}/{key}_w7/meta.pkl", "rb"))["accounting"],
            "accounting_date": pickle.load(open(f"{resdir}/{key}/meta.pkl", "rb"))["accounting"],
        }
        for mech in ("MCAR", "MNAR-out"):
            fs = sorted(glob.glob(f"{resdir}/{key}_w7/{mech}_*.pkl"))
            alt = [pickle.load(open(f, "rb")) for f in fs]
            base = [pickle.load(open(f"{resdir}/{key}/{os.path.basename(f)}", "rb")) for f in fs]
            M = {"masks": len(fs), "tau_hat": [r["info"]["tau_hat"] for r in alt]}
            for s in ("random", "matched", "perturb"):
                M[s] = {
                    k: {
                        "date": float(np.mean([win(r[s], k).mean() for r in base])),
                        "week": float(np.mean([win(r[s], k).mean() for r in alt])),
                    }
                    for k in KEYS
                }
            o[mech] = M
        S[key] = o
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
