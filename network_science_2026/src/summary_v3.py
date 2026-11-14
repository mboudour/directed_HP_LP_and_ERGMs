# ruff: noqa: E501
"""Summarize run_v3 pickles.

Metrics: within-pair concordance (random, matched, perturb, sub), pooled average
precision, top-1 accuracy and MRR on role-assignment sets with two nulls (uniform;
initiator drawn in proportion to observed bill counts). Intervals: bootstrap over
masks (Monte Carlo precision) and a clustered bootstrap that resamples masks and,
within each mask, sponsors with all their hyperarcs. Survival strata and coalition
classes as in summary_v2.

Usage: python summary_v3.py RESULTS_DIR OUT_JSON
"""

import glob
import json
import os
import pickle
import sys

import benchmark
import numpy as np
from aggregate import mean_ci, paired
from sklearn.metrics import average_precision_score

MODELS = ["M4c", "M5", "M6", "M5_t05", "S0", "S1", "SI"]
LOCAL = benchmark.LOCAL + ["sponsor_bills", "observed_fraction", "weighted_footprint"]
KEYS = LOCAL + MODELS
SETS = ["random", "matched", "perturb", "sub"]
CASES = ["s118", "s117", "s116", "h118"]
PAIR_CONTRASTS = [
    ("S1", "M5"),
    ("S1", "aa_total"),
    ("M5", "aa_total"),
    ("S1", "degprod"),
    ("S1", "weighted_footprint"),
    ("S1", "observed_fraction"),
    ("S1", "sponsor_bills"),
    ("S1", "S0"),
    ("M5", "M4c"),
    ("M5", "M5_t05"),
    ("S1", "SI"),
]
ROLE_CONTRASTS = [
    ("S1", "chance"),
    ("M5", "chance"),
    ("M4c", "chance"),
    ("M6", "chance"),
    ("M5_t05", "chance"),
    ("SI", "chance"),
    ("S1", "M5"),
    ("S1", "bills_null"),
    ("S1", "sponsor_bills"),
    ("S1", "sponsor_activity"),
    ("S1", "aa_oi"),
    ("S1", "degprod"),
    ("S1", "SI"),
    ("M6", "M5"),
]


def load(d):
    out = {}
    for f in sorted(glob.glob(f"{d}/M*_*.pkl")):
        r = pickle.load(open(f, "rb"))
        out.setdefault(r["info"]["mech"], []).append(r)
    for m in out:
        out[m].sort(key=lambda r: r["info"]["replicate"])
    return out


def win(pairs, k):
    a = np.array([p[0][k] for p in pairs])
    b = np.array([p[1][k] for p in pairs])
    return (a > b) + 0.5 * (a == b)


def ap(pairs, k):
    y = np.r_[np.ones(len(pairs)), np.zeros(len(pairs))]
    s = np.r_[[p[0][k] for p in pairs], [p[1][k] for p in pairs]]
    return average_precision_score(y, s)


def role_top1(role, k):
    v = []
    for cands, ti, mt in role:
        if k == "chance":
            v.append(1 / len(cands))
        elif k == "bills_null":
            b = np.array(mt["bills"])
            v.append(b[ti] / b.sum() if b.sum() > 0 else 1 / len(cands))
        else:
            v.append(benchmark.role_metrics([c[k] for c in cands], ti)[0])
    return np.array(v)


def role_mrr(role, k):
    if k == "chance":
        return np.array([np.mean(1 / np.arange(1, len(c) + 1)) for c, _, _ in role])
    return np.array([benchmark.role_metrics([c[k] for c in cands], ti)[1] for cands, ti, _ in role])


def cluster_boot(vals_by_mask, sponsors_by_mask, seed=1, B=2000):
    """Sponsor bootstrap: one resample of sponsors per replicate, shared by all masks.

    Each replicate draws the set of sponsors with replacement (multinomial weights) and
    recomputes every mask's mean with all hyperarcs of a sponsor weighted together; the
    replicate value is the average over masks. This reflects the sampling variation of
    the sponsors of the fixed record, which all masks share.
    """
    rng = np.random.default_rng(seed)
    allsp = np.unique(np.concatenate(sponsors_by_mask))
    pos = {v: i for i, v in enumerate(allsp)}
    S = len(allsp)
    sums, cnts = [], []
    for v, sp in zip(vals_by_mask, sponsors_by_mask, strict=False):
        idx = np.array([pos[x] for x in sp])
        sums.append(np.bincount(idx, weights=v, minlength=S))
        cnts.append(np.bincount(idx, minlength=S).astype(float))
    sums, cnts = np.array(sums), np.array(cnts)  # masks x S
    W = rng.multinomial(S, np.full(S, 1 / S), size=B).astype(float)  # B x S
    num = W @ sums.T
    den = W @ cnts.T
    means = np.nanmean(np.where(den > 0, num / np.where(den > 0, den, 1), np.nan), axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def classes(pairs):
    other = np.array([p[2]["other"] for p in pairs])
    size = np.array([p[2]["size"] for p in pairs])
    ps = np.array([p[2]["surv"] for p in pairs])
    ns = np.array([p[2]["neg_surv"] for p in pairs])
    return {
        "bipartisan": other >= 1,
        "single_party": other == 0,
        "bipartisan_20": other / size >= 0.2,
        "bipartisan_size_1_3": (other >= 1) & (size <= 3),
        "single_party_size_1_3": (other == 0) & (size <= 3),
        "bipartisan_size_4_10": (other >= 1) & (size >= 4),
        "single_party_size_4_10": (other == 0) & (size >= 4),
        "pos_not_surv": ~ps,
        "pos_surv": ps,
        "neither_surv": ~ps & ~ns,
    }


CLASS_KEYS = [
    "M4c",
    "M5",
    "S0",
    "S1",
    "SI",
    "party_share",
    "aa_total",
    "degprod",
    "observed_fraction",
    "weighted_footprint",
    "sponsor_bills",
]


def summarize_case(runs):
    out = {}
    for mech, rs in runs.items():
        o = {"masks": len(rs)}
        o["info"] = {
            "evaluated": float(np.mean([r["info"]["evaluated"] for r in rs])),
            "heldout": float(np.mean([r["info"]["heldout"] for r in rs])),
            "tau_hat": [float(r["info"]["tau_hat"]) for r in rs],
            "pairs": {s: float(np.mean([len(r[s]) for r in rs])) for s in SETS},
            "mle_max_gradient": float(
                max(r["info"]["mle"][m]["max_abs_gradient"] for r in rs for m in r["info"]["mle"])
            ),
            "mle_arcs_gap": float(
                max(
                    abs(r["info"]["mle"][m]["expected_arcs"] - r["info"]["mle"][m]["observed_arcs"])
                    for r in rs
                    for m in r["info"]["mle"]
                )
            ),
            "mle_mutual_gap": float(
                max(
                    abs(
                        r["info"]["mle"][m]["expected_mutual"]
                        - r["info"]["mle"][m]["observed_mutual"]
                    )
                    for r in rs
                    for m in r["info"]["mle"]
                )
            ),
            "zero_outdegree": [
                min(r["info"]["mle"]["S1"]["zero_outdegree"] for r in rs),
                max(r["info"]["mle"]["S1"]["zero_outdegree"] for r in rs),
            ],
            "dyads": rs[0]["info"]["mle"]["S1"]["dyads"],
            "head_sizes": np.bincount(
                [p[2]["size"] for p in rs[0]["random"]], minlength=11
            ).tolist(),
        }
        for s in SETS:
            o[s] = {}
            for k in KEYS:
                o[s][k] = {
                    "concordance": mean_ci([win(r[s], k).mean() for r in rs]),
                    "pr_auc": mean_ci([ap(r[s], k) for r in rs]),
                }
            o[s + "_contrasts"] = {}
            spon = [np.array([p[2]["sponsor"] for p in r[s]]) for r in rs]
            for x, y in PAIR_CONTRASTS:
                vec = [win(r[s], x) - win(r[s], y) for r in rs]
                o[s + "_contrasts"][f"{x} - {y}"] = {
                    "concordance": paired([v.mean() for v in vec]),
                    "concordance_cluster": cluster_boot(vec, spon),
                    "pr_auc": paired([ap(r[s], x) - ap(r[s], y) for r in rs]),
                }
            o[s + "_classes"] = {}
            for cname in classes(rs[0][s]):
                sel = [classes(r[s])[cname] for r in rs]
                vals = {}
                for k in CLASS_KEYS:
                    vals[k] = float(
                        np.mean(
                            [
                                win(r[s], k)[m_].mean()
                                for r, m_ in zip(rs, sel, strict=False)
                                if m_.any()
                            ]
                        )
                    )
                cons = {}
                for x, y in [("M5", "M4c"), ("S1", "S0"), ("S1", "M5"), ("S1", "aa_total")]:
                    d = [
                        (win(r[s], x) - win(r[s], y))[m_].mean()
                        for r, m_ in zip(rs, sel, strict=False)
                        if m_.any()
                    ]
                    cons[f"{x} - {y}"] = paired(d)
                o[s + "_classes"][cname] = {
                    "share": float(np.mean([m_.mean() for m_ in sel])),
                    "concordance": vals,
                    "contrasts": cons,
                }
        o["role"] = {}
        for k in KEYS + ["chance", "bills_null"]:
            o["role"][k] = {"top1": mean_ci([role_top1(r["role"], k).mean() for r in rs])}
            if k != "bills_null":
                o["role"][k]["mrr"] = mean_ci([role_mrr(r["role"], k).mean() for r in rs])
        o["role_classes"] = {}
        for cname, fn in [
            ("pair", lambda mt: mt["size"] == 1),
            ("size_2_3", lambda mt: 2 <= mt["size"] <= 3),
            ("size_4_10", lambda mt: mt["size"] >= 4),
            ("bipartisan", lambda mt: mt["other"] >= 1),
            ("single_party", lambda mt: mt["other"] == 0),
        ]:
            o["role_classes"][cname] = {
                "share": float(np.mean([np.mean([fn(mt) for _, _, mt in r["role"]]) for r in rs]))
            }
            for k in ["S1", "M5", "sponsor_bills", "sponsor_activity", "chance", "bills_null"]:
                o["role_classes"][cname][k] = float(
                    np.mean([role_top1([x for x in r["role"] if fn(x[2])], k).mean() for r in rs])
                )
        spon = [np.array([mt["sponsor"] for _, _, mt in r["role"]]) for r in rs]
        o["role_contrasts"] = {}
        for x, y in ROLE_CONTRASTS:
            vec = [role_top1(r["role"], x) - role_top1(r["role"], y) for r in rs]
            o["role_contrasts"][f"{x} - {y}"] = {
                "top1": paired([v.mean() for v in vec]),
                "top1_cluster": cluster_boot(vec, spon),
            }
        th = {}
        for mname in rs[0]["theta"]:
            th[mname] = {
                t: [
                    float(np.mean([r["theta"][mname][t] for r in rs])),
                    float(np.min([r["theta"][mname][t] for r in rs])),
                    float(np.max([r["theta"][mname][t] for r in rs])),
                ]
                for t in rs[0]["theta"][mname]
            }
        o["theta"] = th
        out[mech] = o
    return out


def main(resdir, out_json, cases=None):
    S = json.load(open(out_json)) if os.path.exists(out_json) else {}
    for c in cases or CASES:
        runs = load(f"{resdir}/v3_{c}")
        if len(runs) == 2 and all(len(v) == 30 for v in runs.values()):
            S[c] = summarize_case(runs)
            print("summarized", c, flush=True)
            json.dump(S, open(out_json, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3].split(",") if len(sys.argv) > 3 else None)
