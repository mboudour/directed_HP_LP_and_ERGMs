"""Summarize run_v2 pickles: pooled and within-pair metrics, matched candidates, contrasts.

Within-pair concordance of a score on a candidate set is the share of pairs in
which the recorded hyperarc scores above its alternative (ties count one half).
Intervals: (a) percentile bootstrap over masks (Monte Carlo precision), and
(b) a two-level bootstrap that resamples masks and, within each mask, pairs
(sampling variation of the bills of the record), for concordance contrasts.

Usage: python summary_v2.py RESULTS_DIR OUT_JSON
"""

import glob
import json
import pickle
import sys

import benchmark
import numpy as np
from aggregate import mean_ci, paired
from sklearn.metrics import average_precision_score

MODELS = ["M4c", "M5", "M6", "S0", "S1", "S0mle", "S1mle"]
LOCAL = benchmark.LOCAL + ["sponsor_bills", "observed_fraction"]
KEYS = LOCAL + MODELS
SETS = ["random", "matched", "sub"]
CASES = ["s118", "s117", "s116", "h118"]
PAIR_CONTRASTS = [
    ("S1mle", "M5"),
    ("S1mle", "aa_total"),
    ("S1mle", "degprod"),
    ("S1mle", "sponsor_activity"),
    ("S1mle", "sponsor_bills"),
    ("S1mle", "observed_fraction"),
    ("S1mle", "S0mle"),
    ("S1mle", "S1"),
    ("M5", "M4c"),
    ("degprod", "S0mle"),
]
ROLE_CONTRASTS = [
    ("S1mle", "chance"),
    ("S0mle", "chance"),
    ("M4c", "chance"),
    ("M6", "chance"),
    ("S1mle", "aa_oi"),
    ("S1mle", "aa_total"),
    ("S1mle", "degprod"),
    ("S1mle", "sponsor_activity"),
    ("S1mle", "sponsor_bills"),
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
    if len(pairs) < 2:
        return np.nan
    y = np.r_[np.ones(len(pairs)), np.zeros(len(pairs))]
    s = np.r_[[p[0][k] for p in pairs], [p[1][k] for p in pairs]]
    return average_precision_score(y, s)


def role_top1(role, k):
    v = []
    for cands, ti, _ in role:
        if k == "chance":
            v.append(1 / len(cands))
        else:
            v.append(benchmark.role_metrics([c[k] for c in cands], ti)[0])
    return np.array(v)


def role_mrr(role, k):
    return np.array([benchmark.role_metrics([c[k] for c in cands], ti)[1] for cands, ti, _ in role])


def two_level(per_mask_vectors, seed=1, B=2000):
    """Two-level bootstrap of the mean of per-pair values (masks, then pairs)."""
    rng = np.random.default_rng(seed)
    M = len(per_mask_vectors)
    means = np.empty(B)
    for b in range(B):
        ms = rng.integers(M, size=M)
        tot = 0.0
        for mi in ms:
            v = per_mask_vectors[mi]
            tot += v[rng.integers(len(v), size=len(v))].mean()
        means[b] = tot / M
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def classes(pairs):
    other = np.array([p[2]["other"] for p in pairs])
    size = np.array([p[2]["size"] for p in pairs])
    return {
        "bipartisan": other >= 1,
        "single_party": other == 0,
        "bipartisan_20": other / size >= 0.2,
        "size_1": size == 1,
        "size_2_3": (size >= 2) & (size <= 3),
        "size_4_10": size >= 4,
        "bipartisan_size_4_10": (other >= 1) & (size >= 4),
        "single_party_size_4_10": (other == 0) & (size >= 4),
        "bipartisan_size_1_3": (other >= 1) & (size <= 3),
        "single_party_size_1_3": (other == 0) & (size <= 3),
    }


def summarize_case(runs):
    out = {}
    for mech, rs in runs.items():
        o = {"masks": len(rs)}
        o["info"] = {
            "evaluated": float(np.mean([r["info"]["evaluated"] for r in rs])),
            "heldout": float(np.mean([r["info"]["heldout"] for r in rs])),
            "zero_outdegree": [
                int(min(r["info"]["zero_outdegree"] for r in rs)),
                int(max(r["info"]["zero_outdegree"] for r in rs)),
            ],
            "zero_indegree": [
                int(min(r["info"]["zero_indegree"] for r in rs)),
                int(max(r["info"]["zero_indegree"] for r in rs)),
            ],
            "matched_failed": int(sum(r["info"]["matched_failed"] for r in rs)),
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
            "head_sizes": np.bincount(
                [p[2]["size"] for p in rs[0]["random"]], minlength=11
            ).tolist(),
        }
        for s in SETS:
            o[s] = {}
            for k in KEYS:
                c = [win(r[s], k).mean() for r in rs]
                a = [ap(r[s], k) for r in rs]
                o[s][k] = {"concordance": mean_ci(c), "pr_auc": mean_ci(a)}
            o[s + "_contrasts"] = {}
            for x, y in PAIR_CONTRASTS:
                dc = [win(r[s], x).mean() - win(r[s], y).mean() for r in rs]
                da = [ap(r[s], x) - ap(r[s], y) for r in rs]
                vec = [win(r[s], x) - win(r[s], y) for r in rs]
                o[s + "_contrasts"][f"{x} - {y}"] = {
                    "concordance": paired(dc),
                    "concordance_two_level": two_level(vec),
                    "pr_auc": paired(da),
                }
            # classes
            o[s + "_classes"] = {}
            for cname in classes(rs[0][s]):
                share = float(np.mean([classes(r[s])[cname].mean() for r in rs]))
                vals = {}
                for k in ["M4c", "M5", "S0mle", "S1mle", "party_share", "aa_total", "degprod"]:
                    vals[k] = float(
                        np.mean(
                            [
                                win(r[s], k)[classes(r[s])[cname]].mean()
                                for r in rs
                                if classes(r[s])[cname].any()
                            ]
                        )
                    )
                cons = {}
                for x, y in [("M5", "M4c"), ("S1mle", "S0mle")]:
                    d = [
                        (win(r[s], x) - win(r[s], y))[classes(r[s])[cname]].mean()
                        for r in rs
                        if classes(r[s])[cname].any()
                    ]
                    cons[f"{x} - {y}"] = paired(d)
                o[s + "_classes"][cname] = {"share": share, "concordance": vals, "contrasts": cons}
        # role assignment
        o["role"] = {}
        for k in KEYS + ["chance"]:
            o["role"][k] = {
                "top1": mean_ci([role_top1(r["role"], k).mean() for r in rs]),
                "mrr": mean_ci([role_mrr(r["role"], k).mean() for r in rs])
                if k != "chance"
                else mean_ci(
                    [
                        np.mean([np.mean(1 / np.arange(1, len(c) + 1)) for c, _, _ in r["role"]])
                        for r in rs
                    ]
                ),
            }
        o["role_contrasts"] = {}
        for x, y in ROLE_CONTRASTS:
            d = [role_top1(r["role"], x).mean() - role_top1(r["role"], y).mean() for r in rs]
            vec = [role_top1(r["role"], x) - role_top1(r["role"], y) for r in rs]
            o["role_contrasts"][f"{x} - {y}"] = {
                "top1": paired(d),
                "top1_two_level": two_level(vec),
            }
        # coefficients (non-actor terms), mean and range over masks
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


def main(resdir, out_json):
    S = {}
    for c in CASES:
        runs = load(f"{resdir}/v2_{c}")
        if runs and all(len(v) == 30 for v in runs.values()) and len(runs) == 2:
            S[c] = summarize_case(runs)
            print("summarized", c, flush=True)
    json.dump(S, open(out_json, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
