# ruff: noqa: E501
"""Concordance in the contribution benchmark by kind of committee (FEC committee master file).

Classes: party committees (type X, Y, Z); leadership PACs (designation D); candidate committees
(type H, S, P); corporate PACs (organization C or W); trade, membership and cooperative PACs (T, M, V);
labor PACs (L); other nonconnected committees.

Usage: python summary_fec_types.py RESULTS_DIR DIME OUT_JSON
"""

import glob
import json
import pickle
import sys

import fec_case as F
import numpy as np
from summary_v3 import win

KEYS = ["BS0", "BS1", "BM", "LR", "cofunding", "weighted_footprint"]
ORDER = [
    "corporate",
    "trade/membership",
    "labor",
    "nonconnected",
    "leadership",
    "candidate",
    "party",
]


def kind(case, i):
    t, o, d = case.comm_type[i], case.comm_org[i], case.comm_dsgn[i]
    if t in ("X", "Y", "Z"):
        return "party"
    if d == "D":
        return "leadership"
    if t in ("H", "S", "P"):
        return "candidate"
    if o in ("C", "W"):
        return "corporate"
    if o in ("T", "M", "V"):
        return "trade/membership"
    if o == "L":
        return "labor"
    return "nonconnected"


def main(resdir, dime, out):
    S = {}
    for cyc, key in ((2024, "fec24"), (2022, "fec22")):
        case = F.build_case(f"{resdir}/../fec{key[3:]}", dime, cyc)
        kinds = np.array([kind(case, i) for i in range(case.C)])
        o = {"committees": {k: int((kinds == k).sum()) for k in ORDER}}
        for mech in ("MCAR", "MNAR-out"):
            rs = [
                pickle.load(open(f, "rb"))
                for f in sorted(glob.glob(f"{resdir}/{key}/{mech}_*.pkl"))
            ]
            M = {}
            for s in ("random", "perturb", "matched"):
                M[s] = {}
                for k in ORDER:
                    sel = [np.array([kinds[p[2]["committee"]] == k for p in r[s]]) for r in rs]
                    if not any(x.any() for x in sel):
                        continue
                    cross = [np.array([p[2]["cross"] >= 1 for p in r[s]]) for r in rs]
                    M[s][k] = {
                        "share": float(np.mean([x.mean() for x in sel])),
                        "cross_share": float(
                            np.mean(
                                [c[x].mean() for c, x in zip(cross, sel, strict=True) if x.any()]
                            )
                        ),
                    }
                    for v in KEYS:
                        M[s][k][v] = float(
                            np.mean(
                                [
                                    win(r[s], v)[x].mean()
                                    for r, x in zip(rs, sel, strict=True)
                                    if x.any()
                                ]
                            )
                        )
                    M[s][k]["BS1 - BS0"] = M[s][k]["BS1"] - M[s][k]["BS0"]
            o[mech] = M
        S[key] = o
        print(key, o["committees"], flush=True)
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
