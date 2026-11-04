# ruff: noqa: E501
"""Summary of pairwise and higher-order, undirected and directed models on the co-sponsorship
benchmark: recognition (random, party-matched, head-perturbation sets) and initiator
identification (role-assignment and substitution sets), with sponsor-bootstrap intervals.

Usage: python summary_grid.py RESULTS_DIR OUT_JSON
"""

import json
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot, win

CASES = ["s118", "s117", "s116", "h118"]
REC = ["UM", "M5", "S1", "HM0", "HM", "LR", "coparticipation", "aa_total", "weighted_footprint"]
CONTRASTS = [
    ("HM", "M5"),
    ("HM", "S1"),
    ("HM", "coparticipation"),
    ("HM", "HM0"),
    ("M5", "UM"),
    ("HM", "UM"),
    ("HM", "LR"),
]


def merged(res, case, mech, rep):
    f = f"{mech}_{rep:02d}.pkl"
    a = pickle.load(open(f"{res}/v3_{case}/{f}", "rb"))
    b = pickle.load(open(f"{res}/v4_{case}/{f}", "rb"))
    out = {}
    extra = {k: pickle.load(open(f"{res}/{k}_{case}/{f}", "rb")) for k in ("coal", "hm", "um")}
    for s in ("random", "matched", "perturb"):
        rows = []
        for i, x in enumerate(a[s]):
            p, q = dict(x[0]), dict(x[1])
            for e in extra.values():
                p.update(e[s][i][0])
                q.update(e[s][i][1])
            if s in b:
                p["LR"], q["LR"] = b[s][i][0]["LR"], b[s][i][1]["LR"]
            rows.append((p, q, x[2]["sponsor"]))
        out[s] = rows
    hr = pickle.load(open(f"{res}/hr_{case}/{f}", "rb"))
    out["role"] = [
        (cands, y, hrp) for (cands, y, _), (hrp, _) in zip(a["role"], hr["role"], strict=True)
    ]
    out["role_sponsor"] = [a_meta["sponsor"] for _, _, a_meta in a["role"]]
    out["sub"] = [
        ({**x[0], **h[0]}, {**x[1], **h[1]}, x[2]["sponsor"])
        for x, h in zip(a["sub"], hr["sub"], strict=True)
    ]
    out["hr_theta"] = hr["theta"]
    out["hm_theta"] = pickle.load(open(f"{res}/hm_{case}/{f}", "rb"))["theta"]
    out["um_theta"] = pickle.load(open(f"{res}/um_{case}/{f}", "rb"))["theta"]
    return out


def top1(scores, y, rng):
    s = np.asarray(scores, float)
    best = np.flatnonzero(s == s.max())
    return float(rng.choice(best) == y)


def main(res, out):
    S = {}
    for case in CASES:
        o = {}
        for mech in ("MCAR", "MNAR-out"):
            rs = [merged(res, case, mech, r) for r in range(1, 31)]
            M = {}
            for s in ("random", "matched", "perturb"):
                keys = [k for k in REC if k in rs[0][s][0][0]]
                M[s] = {k: float(np.mean([win(r[s], k).mean() for r in rs])) for k in keys}
                spon = [np.array([p[2] for p in r[s]]) for r in rs]
                M[s + "_contrasts"] = {}
                for x, y in CONTRASTS:
                    if x in keys and y in keys:
                        vec = [win(r[s], x) - win(r[s], y) for r in rs]
                        M[s + "_contrasts"][f"{x} - {y}"] = [
                            float(np.mean([v.mean() for v in vec])),
                            *cluster_boot(vec, spon),
                        ]
            rng = np.random.default_rng(11)
            acc = {k: [] for k in ("HR", "S1", "M5", "sponsor_bills")}
            for r in rs:
                v = {k: [] for k in acc}
                for cands, y, hrp in r["role"]:
                    v["HR"].append(top1(hrp, y, rng))
                    for k in ("S1", "M5", "sponsor_bills"):
                        v[k].append(top1([c[k] for c in cands], y, rng))
                for k in acc:
                    acc[k].append(np.array(v[k]))
            M["role_top1"] = {k: float(np.mean([x.mean() for x in v])) for k, v in acc.items()}
            spon = [np.array(r["role_sponsor"]) for r in rs]
            M["role_contrasts"] = {}
            for x, y in (("HR", "S1"), ("HR", "sponsor_bills"), ("S1", "sponsor_bills")):
                vec = [a - b for a, b in zip(acc[x], acc[y], strict=True)]
                M["role_contrasts"][f"{x} - {y}"] = [
                    float(np.mean([v.mean() for v in vec])),
                    *cluster_boot(vec, spon),
                ]
            M["sub"] = {
                k: float(np.mean([win(r["sub"], k).mean() for r in rs]))
                for k in ("HR", "S1", "M5", "sponsor_bills")
            }
            sp = [np.array([p[2] for p in r["sub"]]) for r in rs]
            vec = [win(r["sub"], "HR") - win(r["sub"], "S1") for r in rs]
            M["sub_contrasts"] = {
                "HR - S1": [float(np.mean([v.mean() for v in vec])), *cluster_boot(vec, sp)]
            }
            M["hr_theta"] = {
                k: float(np.mean([r["hr_theta"][k] for r in rs])) for k in rs[0]["hr_theta"]
            }
            M["hm_theta"] = {
                k: float(np.mean([r["hm_theta"]["HM"][k] for r in rs]))
                for k in rs[0]["hm_theta"]["HM"]
            }
            M["um_theta"] = {
                k: float(np.mean([r["um_theta"]["UM"][k] for r in rs]))
                for k in rs[0]["um_theta"]["UM"]
            }
            M["um_tau"] = [r["um_theta"]["tau"] for r in rs]
            o[mech] = M
        S[case] = o
        print(case, "done", flush=True)
        json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
