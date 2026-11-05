# ruff: noqa: E501
"""Summary of the hidden co-sponsor task (run_member.py).

Ranks: the hidden co-sponsor is the first candidate; ties are resolved by their expected value
under a uniformly random order of the tied candidates. Reports MRR, Recall@1, @5, @10 and mean
rank (means over tasks within a hiding, averaged over hidings) and sponsor- or committee-bootstrap
intervals for paired MRR contrasts, against all 19 alternatives, against the 10 random ones only
and against the 9 most active ones only.

Usage: python summary_member.py RESULTS_DIR OUT_JSON [CASES...]
"""

import json
import os
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot

SUBSETS = {"all": lambda row: row, "random": lambda row: [row[0], *row[10:]], "hard": lambda row: row[:10]}
KEYS = ["NHPD_maxmin", "NHPD_mean", "HM", "UM", "M5", "S1", "BM", "BS1", "LR", "coparticipation", "aa_total", "cofunding", "path3", "weighted_pair", "hpra", "cocitation", "indegree"]
CONTRASTS = [("HM", "coparticipation"), ("HM", "weighted_pair"), ("HM", "NHPD_maxmin"), ("HM", "NHPD_mean"), ("HM", "M5"), ("HM", "hpra"), ("NHPD_maxmin", "hpra"), ("M5", "hpra"), ("UM", "HM"), ("NHPD_maxmin", "M5"), ("NHPD_maxmin", "LR"), ("NHPD_maxmin", "coparticipation"), ("LR", "coparticipation"), ("NHPD_maxmin", "BM"), ("LR", "BM"), ("weighted_pair", "BM"), ("LR", "cofunding"), ("cofunding", "BM"), ("NHPD_maxmin", "cofunding"), ("BM", "BS1")]


def rank_stats(vals):
    v = np.asarray(vals, float)
    g = int((v[1:] > v[0]).sum())
    t = int((v[1:] == v[0]).sum()) + 1
    pos = np.arange(g + 1, g + t + 1)
    return float(np.mean(1 / pos)), float(np.mean(pos == 1)), float(np.mean(pos <= 5)), float(np.mean(pos <= 10)), float(pos.mean())


def load(res, case, reps):
    out = {}
    for mech in ("MCAR", "MNAR-out"):
        rs = []
        for r in range(1, reps + 1):
            f = f"{res}/member_{case}/{mech}_{r:02d}.pkl"
            if os.path.exists(f):
                rs.append(pickle.load(open(f, "rb")))
        out[mech] = rs
    return out


def main(res, out_json, cases=("s118", "s117", "s116", "h118", "fec24", "fec22"), reps=10):
    S = {}
    for case in cases:
        D = load(res, case, reps)
        if not D["MCAR"]:
            continue
        S[case] = {}
        for mech, rs in D.items():
            if not rs:
                continue
            keys = [k for k in KEYS if k in rs[0]["scores"][0][0]]
            spon = [np.array(r["sponsor"]) for r in rs]
            M = {"hidings": len(rs), "tasks": float(np.mean([len(r["scores"]) for r in rs]))}
            for sub, f in SUBSETS.items():
                stats = {k: [np.array([rank_stats([c[k] for c in f(row)]) for row in r["scores"]]) for r in rs] for k in keys}
                M[sub] = {}
                for k in keys:
                    arr = np.array([x.mean(0) for x in stats[k]])
                    M[sub][k] = dict(zip(["mrr", "r1", "r5", "r10", "mean_rank"], arr.mean(0).tolist(), strict=True))
                M[sub]["contrasts"] = {}
                for x, y in CONTRASTS:
                    if x in keys and y in keys:
                        vec = [a[:, 0] - b[:, 0] for a, b in zip(stats[x], stats[y], strict=True)]
                        M[sub]["contrasts"][f"{x} - {y}"] = [float(np.mean([v.mean() for v in vec])), *cluster_boot(vec, spon)]
            S[case][mech] = M
    json.dump(S, open(out_json, "w"), indent=1)
    return S


if __name__ == "__main__":
    a = sys.argv
    S = main(a[1], a[2], tuple(a[3:]) if len(a) > 3 else ("s118", "s117", "s116", "h118", "fec24", "fec22"))
    for c, o in S.items():
        for m, M in o.items():
            for sub in SUBSETS:
                print(c, m, sub, M["hidings"], int(M["tasks"]), {k: round(v["mrr"], 3) for k, v in M[sub].items() if k != "contrasts"})
