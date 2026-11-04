# ruff: noqa: E501
"""Summarize the FEC benchmark and compare recorded hyperarcs with generated concepts.

Usage: python summary_fec.py FEC24_DIR FEC22_DIR DIME RESULTS_DIR OUT_JSON
"""

import glob
import json
import os
import pickle
import sys

import fec_case as F
import numpy as np
from summary_v3 import cluster_boot, win

KEYS = [
    "BM",
    "BM_t05",
    "BS0",
    "BS1",
    "LR",
    "coparticipation",
    "bipartite_aa",
    "activity",
    "popularity",
    "degprod",
    "path3",
    "cofunding",
    "alignment",
    "proximity",
    "weighted_footprint",
    "observed_fraction",
    "bill_count",
]
LOCAL = [
    "activity",
    "popularity",
    "degprod",
    "path3",
    "cofunding",
    "alignment",
    "proximity",
    "weighted_footprint",
    "observed_fraction",
    "bill_count",
]
CONTRASTS = [
    ("coparticipation", "BM"),
    ("coparticipation", "BS1"),
    ("coparticipation", "cofunding"),
    ("LR", "coparticipation"),
    ("BS1", "BM"),
    ("BM", "cofunding"),
    ("BS1", "cofunding"),
    ("LR", "cofunding"),
    ("LR", "BS1"),
    ("BM", "BM_t05"),
    ("BS1", "BS0"),
    ("BM", "path3"),
    ("BS1", "weighted_footprint"),
]


def closure(case):
    Y = np.zeros((case.C, case.K), bool)
    for s, H in case.types:
        Y[s, list(H)] = True
    eq, tails, jac, ratio = [], [], [], []
    for s, H in case.types:
        Hl = sorted(H)
        Td = np.nonzero(Y[:, Hl].all(1))[0]
        Hs = np.nonzero(Y[Td].all(0))[0]
        eq.append(len(Td) == 1 and len(Hs) == len(Hl))
        tails.append(len(Td))
        fp = {(s, h) for h in Hl}
        fc = {(i, j) for i in Td for j in Hs}
        jac.append(len(fp & fc) / len(fp | fc))
        ratio.append(len(Hl) / Y[s].sum())
    return {
        "share_equal": float(np.mean(eq)),
        "mean_tail": float(np.mean(tails)),
        "median_tail": float(np.median(tails)),
        "mean_jaccard": float(np.mean(jac)),
        "mean_head_over_outneighbourhood": float(np.mean(ratio)),
    }


def main(f24, f22, dime, resdir, out):
    S = {}
    for cyc, fdir in [(2024, f24), (2022, f22)]:
        key = f"fec{str(cyc)[2:]}"
        case = F.build_case(fdir, dime, cyc)
        o = {
            "accounting": case.accounting,
            "cf_missing": case.cand_cf_missing,
            "closure": closure(case),
        }
        o["head_sizes"] = np.bincount([len(H) for _, H in case.types], minlength=11).tolist()
        for mech in ["MCAR", "MNAR-out"]:
            fs = sorted(glob.glob(f"{resdir}/{key}/{mech}_*.pkl"))
            rs = [pickle.load(open(f, "rb")) for f in fs]
            for r, f in zip(rs, fs, strict=True):
                c = pickle.load(open(f"{resdir}/coal_{key}/{os.path.basename(f)}", "rb"))
                for s_ in ("random", "matched", "perturb"):
                    assert len(c[s_]) == len(r[s_])
                    r[s_] = [
                        ({**p[0], **q[0]}, {**p[1], **q[1]}, p[2])
                        for p, q in zip(r[s_], c[s_], strict=True)
                    ]
            M = {
                "masks": len(rs),
                "tau_hat": [r["info"]["tau_hat"] for r in rs],
                "evaluated": float(np.mean([r["info"]["evaluated"] for r in rs])),
                "heldout": float(np.mean([r["info"]["heldout"] for r in rs])),
            }
            for s in ["random", "matched", "perturb"]:
                M[s] = {k: float(np.mean([win(r[s], k).mean() for r in rs])) for k in KEYS}
                M[s + "_best_local"] = max(LOCAL, key=lambda k: M[s][k])
                spon = [np.array([p[2]["committee"] for p in r[s]]) for r in rs]
                M[s + "_contrasts"] = {}
                for x, y in CONTRASTS:
                    vec = [win(r[s], x) - win(r[s], y) for r in rs]
                    M[s + "_contrasts"][f"{x} - {y}"] = [
                        float(np.mean([v.mean() for v in vec])),
                        *cluster_boot(vec, spon),
                    ]
                cls = {}
                for cname, fn in [
                    ("cross", lambda mt: mt["cross"] >= 1),
                    ("aligned", lambda mt: mt["cross"] == 0),
                    ("pos_not_surv", lambda mt: not mt["surv"]),
                ]:
                    sel = [np.array([fn(p[2]) for p in r[s]]) for r in rs]
                    cls[cname] = {
                        "share": float(np.mean([x.mean() for x in sel])),
                        **{
                            k: float(
                                np.mean(
                                    [
                                        win(r[s], k)[x].mean()
                                        for r, x in zip(rs, sel, strict=False)
                                        if x.any()
                                    ]
                                )
                            )
                            for k in [
                                "BM",
                                "BS0",
                                "BS1",
                                "LR",
                                "cofunding",
                                "weighted_footprint",
                                "observed_fraction",
                            ]
                        },
                        "BS1 - BS0": float(
                            np.mean(
                                [
                                    (win(r[s], "BS1") - win(r[s], "BS0"))[x].mean()
                                    for r, x in zip(rs, sel, strict=False)
                                    if x.any()
                                ]
                            )
                        ),
                    }
                M[s + "_classes"] = cls
            M["theta"] = {
                k: np.mean([r["theta"][k] for r in rs], 0).tolist() for k in rs[0]["theta"]
            }
            o[mech] = M
        S[key] = o
        print(key, "done", flush=True)
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:6])
