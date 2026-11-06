# ruff: noqa: E501
"""Summary of run_member_full.py: the hidden-supporter task ranked against all active
non-participants (full), against the 19 alternatives of run_member.py (twenty), against the 10
random alternatives (random) and the 9 most active (hard), with NHP-D trained on the 9+10 design
(NHPD_*) and on 19 random alternatives (NHPD_*_r).

Reports MRR, Recall@1, Recall@10 and mean rank per method, separately for tasks whose hidden
supporter is or is not one of the nine most active legislators, and sponsor-bootstrap intervals
for paired MRR contrasts.

Usage: python summary_member_full.py RESULTS_DIR OUT_JSON [REPS]
"""

import json
import os
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot

CASES = ["s118", "s117", "s116", "h118"]
SUBS = ["full", "twenty", "random", "hard"]
CONTRASTS = [("HM", "NHPD_maxmin"), ("HM", "NHPD_maxmin_r"), ("HM", "NHPD_mean_r"), ("HM", "M5"), ("HM", "coparticipation"), ("HM", "UM"), ("coparticipation", "NHPD_maxmin_r"), ("NHPD_maxmin_r", "NHPD_maxmin"), ("NHPD_mean_r", "NHPD_mean"), ("M5", "NHPD_maxmin_r")]


def main(res, out, reps=10):
    S = {}
    for case in CASES:
        S[case] = {}
        for mech in ("MCAR", "MNAR-out"):
            rs = [pickle.load(open(f"{res}/full_{case}/{mech}_{r:02d}.pkl", "rb")) for r in range(1, reps + 1) if os.path.exists(f"{res}/full_{case}/{mech}_{r:02d}.pkl")]
            if not rs:
                continue
            keys = list(rs[0]["ranks"])
            M = {"hidings": len(rs), "tasks": float(np.mean([r["info"]["tasks"] for r in rs])), "n_alt_full": float(np.mean([r["info"]["n_alt_full"] for r in rs])), "share_top9": float(np.mean([np.mean(r["target_top9"]) for r in rs]))}
            for sub in SUBS:
                M[sub] = {}
                for k in keys:
                    rr = [r["ranks"][k][sub][:, 0] for r in rs]
                    rk = [r["ranks"][k][sub][:, 1] for r in rs]
                    M[sub][k] = {
                        "mrr": float(np.mean([x.mean() for x in rr])),
                        "r1": float(np.mean([np.mean(x <= 1) for x in rk])),
                        "r10": float(np.mean([np.mean(x <= 10) for x in rk])),
                        "mean_rank": float(np.mean([x.mean() for x in rk])),
                    }
                    if sub == "full":
                        top = [np.asarray(r["target_top9"]) for r in rs]
                        M[sub][k]["mrr_top9"] = float(np.mean([x[t].mean() for x, t in zip(rr, top, strict=True) if t.any()]))
                        M[sub][k]["mrr_other"] = float(np.mean([x[~t].mean() for x, t in zip(rr, top, strict=True)]))
                spon = [np.array(r["sponsor"]) for r in rs]
                M[sub]["contrasts"] = {}
                for x, y in CONTRASTS:
                    if x in keys and y in keys:
                        vec = [r["ranks"][x][sub][:, 0] - r["ranks"][y][sub][:, 0] for r in rs]
                        M[sub]["contrasts"][f"{x} - {y}"] = [float(np.mean([v.mean() for v in vec])), *cluster_boot(vec, spon)]
            S[case][mech] = M
    json.dump(S, open(out, "w"), indent=1)
    return S


if __name__ == "__main__":
    a = sys.argv
    S = main(a[1], a[2], int(a[3]) if len(a) > 3 else 10)
    for c, o in S.items():
        for m, M in o.items():
            print(c, m, M["hidings"], round(M["n_alt_full"]), {k: round(v["mrr"], 3) for k, v in M["full"].items() if k != "contrasts"})
