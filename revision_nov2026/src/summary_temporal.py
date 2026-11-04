# ruff: noqa: E501
"""Summary of the temporal forecasting benchmark (one split: train on quarters 0-5, forecast
quarters 6-7), with sponsor- or committee-bootstrap intervals for paired contrasts.

Usage: python summary_temporal.py RESULTS_DIR OUT_JSON
"""

import json
import os
import pickle
import sys

import numpy as np
from summary_v3 import win


def boot(vec, groups, B=2000, seed=1):
    rng = np.random.default_rng(seed)
    g = np.unique(groups)
    idx = {v: i for i, v in enumerate(g)}
    gi = np.array([idx[v] for v in groups])
    sums = np.bincount(gi, weights=vec, minlength=len(g))
    cnts = np.bincount(gi, minlength=len(g)).astype(float)
    W = rng.multinomial(len(g), np.ones(len(g)) / len(g), size=B)
    reps = (W @ sums) / (W @ cnts)
    return [float(np.mean(vec)), float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))]


def top1(cands, y, k, rng):
    v = np.array([c[k] for c in cands])
    b = np.flatnonzero(v == v.max())
    return float(rng.choice(b) == y)


def main(res, out):
    S = {}
    for case in ("s118", "h118"):
        f = f"{res}/temporal_{case}/scores.pkl"
        if not os.path.exists(f):
            continue
        r = pickle.load(open(f, "rb"))
        keys = [
            "TERGM",
            "M5",
            "S1",
            "HM",
            "UM",
            "coparticipation",
            "aa_total",
            "weighted_footprint",
        ]
        o = {"info": r["info"]}
        for s in ("random", "matched", "perturb"):
            o[s] = {k: float(win(r[s], k).mean()) for k in keys}
            g = np.array([p[2]["sponsor"] for p in r[s]])
            o[s + "_contrasts"] = {
                f"{x} - {y}": boot(win(r[s], x) - win(r[s], y), g)
                for x, y in (
                    ("TERGM", "M5"),
                    ("TERGM", "S1"),
                    ("HM", "TERGM"),
                    ("HM", "M5"),
                    ("coparticipation", "TERGM"),
                )
            }
        rng = np.random.default_rng(3)
        acc = {
            k: np.array([top1(c, y, k, rng) for c, y, _ in r["role"]])
            for k in ("TERGM", "S1", "M5", "sponsor_bills")
        }
        g = np.array([sp for _, _, sp in r["role"]])
        o["role_top1"] = {k: float(v.mean()) for k, v in acc.items()}
        o["role_chance"] = float(np.mean([1 / len(c) for c, _, _ in r["role"]]))
        o["role_contrasts"] = {
            f"{x} - {y}": boot(acc[x] - acc[y], g)
            for x, y in (("TERGM", "S1"), ("TERGM", "sponsor_bills"), ("S1", "sponsor_bills"))
        }
        coef = f"{res}/temporal_{case}/tergm_coef.csv"
        if os.path.exists(coef):
            import csv

            o["tergm_coef"] = [row for row in csv.reader(open(coef))]
        S[case] = o
    for key in ("fec24", "fec22"):
        f = f"{res}/temporal_{key}/scores.pkl"
        if not os.path.exists(f):
            continue
        r = pickle.load(open(f, "rb"))
        keys = ["TERGM", "BS1", "BM", "LR", "cofunding", "path3", "weighted_footprint"]
        o = {"info": r["info"]}
        for s in ("random", "matched", "perturb"):
            o[s] = {k: float(win(r[s], k).mean()) for k in keys}
            g = np.array([p[2]["committee"] for p in r[s]])
            o[s + "_contrasts"] = {
                f"{x} - {y}": boot(win(r[s], x) - win(r[s], y), g)
                for x, y in (
                    ("TERGM", "BS1"),
                    ("TERGM", "BM"),
                    ("TERGM", "cofunding"),
                    ("LR", "TERGM"),
                )
            }
        coef = f"{res}/temporal_{key}/tergm_coef.csv"
        if os.path.exists(coef):
            import csv

            o["tergm_coef"] = [row for row in csv.reader(open(coef))]
        S[key] = o
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
