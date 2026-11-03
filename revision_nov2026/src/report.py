"""Summaries for one case: per-mask metrics, paired contrasts, role, strata, bipartisan."""

import json
import pickle
import sys

import aggregate as ag
import numpy as np

SCORES = [
    "M0_L1g",
    "M1_L1g",
    "M2_L1g",
    "M3_L1g",
    "M4_L1g",
    "M4c_L1g",
    "M4c_nomut_L1g",
    "M5_L1g",
    "M6_L1g",
    "M4c_L1",
    "M4c_L2",
    "aa_total",
    "aa_oi",
    "aa_oo",
    "aa_ii",
    "cn_total",
    "cn_oi",
    "degprod",
    "reverse",
    "sponsor_activity",
    "cosponsor_popularity",
    "party_share",
]
CONTRASTS = [
    ("M4c_L1g", "M0_L1g"),
    ("M5_L1g", "M4c_L1g"),
    ("M6_L1g", "M5_L1g"),
    ("M4c_nomut_L1g", "M4c_L1g"),
    ("aa_total", "M5_L1g"),
    ("aa_total", "M6_L1g"),
    ("degprod", "M5_L1g"),
    ("degprod", "M6_L1g"),
    ("M4c_L1g", "degprod"),
    ("sponsor_activity", "M5_L1g"),
    ("sponsor_activity", "degprod"),
    ("cosponsor_popularity", "M5_L1g"),
    ("party_share", "M5_L1g"),
    ("aa_total", "degprod"),
]
ROLE = [
    "M4c_L1g",
    "M5_L1g",
    "M6_L1g",
    "aa_oi",
    "aa_total",
    "degprod",
    "sponsor_activity",
    "cosponsor_popularity",
    "cn_oi",
    "reverse",
]
WIN = ["M4c_L1g", "M5_L1g", "M6_L1g", "degprod", "aa_total", "sponsor_activity"]


def _extend(r):
    """Add sender-receiver model scores and contrasts when present in the run."""
    keys = r["random"][0][0].keys()
    for m in ["S0", "S1", "S2", "S3"]:
        k = f"{m}_L1g"
        if k in keys and k not in SCORES:
            SCORES.append(k)
            ROLE.append(k)
            WIN.append(k)
    extra = [
        ("S1_L1g", "M5_L1g"),
        ("S2_L1g", "S1_L1g"),
        ("S3_L1g", "S1_L1g"),
        ("S1_L1g", "S0_L1g"),
        ("aa_total", "S1_L1g"),
        ("degprod", "S1_L1g"),
        ("sponsor_activity", "S1_L1g"),
        ("S1_L1g", "M0_L1g"),
        ("degprod", "S0_L1g"),
    ]
    for a, b in extra:
        if a in SCORES and b in SCORES and (a, b) not in CONTRASTS:
            CONTRASTS.append((a, b))
    for k in list(SCORES):
        if k not in keys:
            SCORES.remove(k)
    for lst in (ROLE, WIN):
        for k in list(lst):
            if k not in keys:
                lst.remove(k)
    for c in list(CONTRASTS):
        if c[0] not in keys or c[1] not in keys:
            CONTRASTS.remove(c)


def build(outdir, caucus):
    res = ag.load(outdir)
    _extend(next(iter(res.values())))
    meta = pickle.load(open(f"{outdir}/meta.pkl", "rb"))
    S = {"meta": meta, "mechs": {}}
    for mech in ["MCAR", "MNAR-out"]:
        reps = sorted(k[1] for k in res if k[0] == mech)
        R = [res[(mech, k)] for k in reps]
        M = {"n_masks": len(R)}
        M["realisation"] = {
            k: float(np.mean([r["info"][k] for r in R]))
            for k in ["types_withheld", "records_withheld", "arc_removal"]
        }
        M["realisation"]["eligible_share"] = float(
            np.mean([r["info"]["eligible_heldout"] / r["info"]["heldout"] for r in R])
        )
        M["realisation"]["surviving_footprint_share"] = float(
            np.mean([r["info"]["surviving_footprints"] / r["info"]["heldout"] for r in R])
        )
        M["pairs"] = {p: float(np.mean([len(r[p]) for r in R])) for p in ["random", "sub", "role"]}
        per = {
            p: {k: [ag.panel_metric(r[p], k) for r in R] for k in SCORES} for p in ["random", "sub"]
        }
        M["pr_auc"] = {
            p: {k: float(np.mean([x[0] for x in per[p][k]])) for k in SCORES} for p in per
        }
        M["roc_auc"] = {
            p: {k: float(np.mean([x[1] for x in per[p][k]])) for k in SCORES} for p in per
        }
        M["contrasts"] = {
            p: {
                f"{a} - {b}": ag.paired(
                    [x[0] - y[0] for x, y in zip(per[p][a], per[p][b], strict=False)]
                )
                for a, b in CONTRASTS
            }
            for p in per
        }
        # role
        rm = [ag.role_metrics(r, ROLE) for r in R]
        M["role"] = {
            k: {
                "top1": float(np.mean([x[k][0] for x in rm])),
                "mrr": float(np.mean([x[k][1] for x in rm])),
            }
            for k in ROLE + ["uniform"]
        }
        M["role_vs_uniform"] = {
            k: {
                "top1": ag.paired([x[k][0] - x["uniform"][0] for x in rm]),
                "mrr": ag.paired([x[k][1] - x["uniform"][1] for x in rm]),
            }
            for k in ROLE
        }
        # survival strata
        st = [ag.strata(r, WIN) for r in R]
        M["strata_share"] = {g: float(np.mean([s[0][g] for s in st])) for g in st[0][0]}
        M["strata_win"] = {
            k: {
                g: ag.mean_ci([s[1][k][g] for s in st if not np.isnan(s[1][k][g])])
                for g in ["true_only", "sub_only", "both", "neither"]
            }
            for k in WIN
        }
        # bipartisan split
        B = {}
        for p in ["random", "sub"]:
            flags = [ag.bip_flags(r, caucus)[p] for r in R]
            B[p] = {"share_bipartisan": float(np.mean([f.mean() for f in flags]))}
            for lab, fn in [("bipartisan", lambda f: f), ("single_party", lambda f: ~f)]:
                vals = {
                    k: [ag.panel_metric(r[p], k, fn(f)) for r, f in zip(R, flags, strict=False)]
                    for k in SCORES
                }
                B[p][lab] = {k: float(np.mean([v[0] for v in vals[k]])) for k in SCORES}
                B[p][lab + "_contrasts"] = {
                    f"{a} - {b}": ag.paired(
                        [x[0] - y[0] for x, y in zip(vals[a], vals[b], strict=False)]
                    )
                    for a, b in [
                        ("M5_L1g", "M4c_L1g"),
                        ("aa_total", "M5_L1g"),
                        ("degprod", "M5_L1g"),
                        ("party_share", "M0_L1g"),
                        ("S1_L1g", "S0_L1g"),
                        ("S1_L1g", "M5_L1g"),
                        ("degprod", "S1_L1g"),
                    ]
                    if a in SCORES and b in SCORES
                }
        M["bipartisan"] = B
        # coefficients
        th = {m: np.array([r["theta"][m] for r in R]) for m in R[0]["theta"]}
        M["theta_mean"] = {m: v.mean(0).tolist() for m, v in th.items()}
        M["theta_sd"] = {m: v.std(0).tolist() for m, v in th.items()}
        S["mechs"][mech] = M
    return S


if __name__ == "__main__":
    import runlib

    name, outdir = sys.argv[1], sys.argv[2]
    case = (
        runlib.make_case(name[:-4], head_cap=3)
        if name.endswith("cap3")
        else runlib.make_case(name[:-5] if name.endswith("uncap") else name)
    )
    S = build(outdir, case.cov["caucus"])
    json.dump(S, open(f"{outdir}/summary.json", "w"), indent=1, default=float)
    print("written", f"{outdir}/summary.json")
