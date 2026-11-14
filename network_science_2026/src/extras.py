"""Transitive-triple check, arc-first static diagnostic, and export for R (MCMC-MLE/gof)."""

import csv
import json
import os
import sys

import ergm
import numpy as np
import runlib
from sklearn.metrics import average_precision_score, roc_auc_score


def training(case, mech, rep):
    m, _ = case.mask(mech, rep)
    Y = np.zeros((case.n, case.n), np.int8)
    for (s, H), mm in zip(case.types, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
    return Y


def main(name, outdir, rexport):
    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    out = {"ttriple": {}, "static": {}}
    for mech in ["MCAR", "MNAR-out"]:
        th = []
        for rep in range(1, 31):
            Y = training(case, mech, rep)
            X, y, _ = ergm.design(Y, ergm.LADDER["TT"])
            b, _ = ergm.mple(X, y)
            th.append(b[1])
        th = np.array(th)
        out["ttriple"][mech] = {
            "fits": len(th),
            "positive": int((th > 0).sum()),
            "mean": float(th.mean()),
            "sd": float(th.std(ddof=1)),
            "min": float(th.min()),
            "max": float(th.max()),
        }
    # arc-first static diagnostic: 30 MCAR splits of the complete cap-eligible projection
    Yf = case.Ycap
    arcs = np.argwhere(Yf == 1)
    non = np.argwhere((Yf == 0) & ~np.eye(case.n, dtype=bool))
    res = {m: [] for m in ["M0", "M1", "M2", "M3", "M4", "M4c", "M5"]}
    for rep in range(1, 31):
        rng = np.random.default_rng(910_000 + rep)
        k = int(np.floor(0.3 * len(arcs)))
        held = arcs[rng.choice(len(arcs), k, replace=False)]
        Y = Yf.copy()
        Y[held[:, 0], held[:, 1]] = 0
        negs = non[rng.choice(len(non), k, replace=False)]
        for m in res:
            X, y, _ = ergm.design(Y, ergm.LADDER[m], case.cov)
            b, _ = ergm.mple(X, y)
            P, _ = ergm.conditional_probs(Y, ergm.LADDER[m], b, case.cov)
            sc = np.r_[P[held[:, 0], held[:, 1]], P[negs[:, 0], negs[:, 1]]]
            lab = np.r_[np.ones(k), np.zeros(k)]
            res[m].append((average_precision_score(lab, sc), roc_auc_score(lab, sc)))
    out["static"] = {
        m: {
            "pr_auc": float(np.mean([x[0] for x in v])),
            "pr_sd": float(np.std([x[0] for x in v], ddof=1)),
            "roc_auc": float(np.mean([x[1] for x in v])),
        }
        for m, v in res.items()
    }
    json.dump(out, open(f"{outdir}/extras.json", "w"), indent=1)
    # export for R
    os.makedirs(rexport, exist_ok=True)
    with open(f"{rexport}/nodes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "party", "state", "nominate", "majority", "seniority"])
        for i in range(case.n):
            w.writerow(
                [
                    i,
                    int(case.cov["party"][i]),
                    int(case.cov["state"][i]),
                    case.cov["nominate"][i],
                    int(case.cov["majority"][i]),
                    case.cov["seniority"][i],
                ]
            )
    nets = {
        "complete": case.Ycap,
        "mcar01": training(case, "MCAR", 1),
        "mnarout01": training(case, "MNAR-out", 1),
    }
    for k, Y in nets.items():
        with open(f"{rexport}/{k}_arcs.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["tail", "head"])
            for i, j in np.argwhere(Y == 1):
                w.writerow([int(i), int(j)])
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
