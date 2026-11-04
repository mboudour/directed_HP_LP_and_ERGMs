# ruff: noqa: E501
"""Summarize run_v4 (decay ablation, supervised baseline) merged with run_v3 scores.

Pairs and role sets of the two runs are built in the same order from the same masks and
candidates; v4 scores are added to the v3 score dictionaries with the prefix "a:" (for
example "a:M2", "a:M5_esp05", "a:LR").

Usage: python summary_v4.py RESULTS_DIR OUT_JSON
"""

import json
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot, role_mrr, role_top1, win

CASES = ["s118", "s117", "s116", "h118"]
SETS = ["random", "perturb", "sub"]
V4 = ["a:M2", "a:M3", "a:M4", "a:M4c", "a:M5", "a:M5_deg05", "a:M5_esp05", "a:LR"]
V3 = [
    "M5",
    "S1",
    "aa_total",
    "aa_oi",
    "degprod",
    "sponsor_activity",
    "sponsor_bills",
    "weighted_footprint",
    "cosponsor_popularity",
]
CONTRASTS = [
    ("a:LR", "S1"),
    ("a:LR", "M5"),
    ("a:LR", "aa_total"),
    ("a:M5_esp05", "M5"),
    ("a:M2", "M5"),
    ("S1", "sponsor_bills"),
    ("M5", "sponsor_bills"),
]


def merge(r3, r4):
    out = {}
    for s in SETS:
        a, b = r3[s], r4[s]
        assert len(a) == len(b)
        out[s] = [
            (
                {**p3[0], **{"a:" + k: v for k, v in p4[0].items()}},
                {**p3[1], **{"a:" + k: v for k, v in p4[1].items()}},
                p3[2],
            )
            for p3, p4 in zip(a, b, strict=False)
        ]
    role = []
    for (c3, t3, m3), (c4, t4, _) in zip(r3["role"], r4["role"], strict=False):
        assert t3 == t4 and len(c3) == len(c4)
        role.append(
            (
                [
                    {**x, **{"a:" + k: v for k, v in y.items()}}
                    for x, y in zip(c3, c4, strict=False)
                ],
                t3,
                m3,
            )
        )
    out["role"] = role
    return out


def main(resdir, out_json):
    S = {}
    for c in CASES:
        S[c] = {}
        for mech in ["MCAR", "MNAR-out"]:
            rs = []
            for rep in range(1, 31):
                r3 = pickle.load(open(f"{resdir}/v3_{c}/{mech}_{rep:02d}.pkl", "rb"))
                r4 = pickle.load(open(f"{resdir}/v4_{c}/{mech}_{rep:02d}.pkl", "rb"))
                rs.append(merge(r3, r4))
            o = {}
            for s in SETS:
                o[s] = {k: float(np.mean([win(r[s], k).mean() for r in rs])) for k in V4 + V3}
                spon = [np.array([p[2]["sponsor"] for p in r[s]]) for r in rs]
                o[s + "_contrasts"] = {}
                for x, y in CONTRASTS:
                    vec = [win(r[s], x) - win(r[s], y) for r in rs]
                    o[s + "_contrasts"][f"{x} - {y}"] = [
                        float(np.mean([v.mean() for v in vec])),
                        *cluster_boot(vec, spon),
                    ]
            o["role"] = {
                k: float(np.mean([role_top1(r["role"], k).mean() for r in rs]))
                for k in V4 + V3 + ["chance", "bills_null"]
            }
            o["role_mrr"] = {
                k: float(np.mean([role_mrr(r["role"], k).mean() for r in rs]))
                for k in V4 + V3 + ["chance"]
            }
            spon = [np.array([mt["sponsor"] for _, _, mt in r["role"]]) for r in rs]
            o["role_contrasts"] = {}
            for x, y in CONTRASTS + [
                ("S1", "chance"),
                ("a:LR", "chance"),
                ("a:LR", "sponsor_bills"),
            ]:
                vec = [role_top1(r["role"], x) - role_top1(r["role"], y) for r in rs]
                o["role_contrasts"][f"{x} - {y}"] = [
                    float(np.mean([v.mean() for v in vec])),
                    *cluster_boot(vec, spon),
                ]
            o["theta_M2"] = {
                t: float(
                    np.mean(
                        [
                            pickle.load(open(f"{resdir}/v4_{c}/{mech}_{rep:02d}.pkl", "rb"))[
                                "theta"
                            ]["M2"][t]
                            for rep in (1, 2, 3)
                        ]
                    )
                )
                for t in ["gwodegree", "gwidegree"]
            }
            S[c][mech] = o
            print(c, mech, flush=True)
    json.dump(S, open(out_json, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
