# ruff: noqa: E501
"""Concordance of the coalition-aware and item-based scores, and paired contrasts with the
models, for co-sponsorship (run_v3/run_v4 pairs) and contributions (run_fec pairs).

Usage: python summary_coal.py RESULTS_DIR OUT_JSON
"""

import json
import pickle
import sys

import numpy as np
from summary_v3 import cluster_boot, win


def merged(resdir, case, mech, rep, fec):
    f = f"{mech}_{rep:02d}.pkl"
    if fec:
        a = pickle.load(open(f"{resdir}/{case}/{f}", "rb"))
        c = pickle.load(open(f"{resdir}/coal_{case}/{f}", "rb"))
        out = {}
        for s in ("random", "matched", "perturb"):
            out[s] = [
                ({**x[0], **y[0]}, {**x[1], **y[1]}, x[2]["committee"])
                for x, y in zip(a[s], c[s], strict=True)
            ]
        return out
    a = pickle.load(open(f"{resdir}/v3_{case}/{f}", "rb"))
    b = pickle.load(open(f"{resdir}/v4_{case}/{f}", "rb"))
    c = pickle.load(open(f"{resdir}/coal_{case}/{f}", "rb"))
    out = {}
    for s in ("random", "matched", "perturb"):
        rows = []
        for i, (x, y) in enumerate(zip(a[s], c[s], strict=True)):
            p, q = {**x[0], **y[0]}, {**x[1], **y[1]}
            if s in b:
                z = b[s][i]
                assert abs(z[0]["M5"] - x[0]["M5"]) < 1e-9 and abs(z[1]["M5"] - x[1]["M5"]) < 1e-9
                p["LR"], q["LR"] = z[0]["LR"], z[1]["LR"]
            rows.append((p, q, x[2]["sponsor"]))
        out[s] = rows
    return out


def main(resdir, out, only=None):
    S = {}
    specs = [(c, False, 30) for c in ("s118", "s117", "s116", "h118")] + [
        (c, True, 20) for c in ("fec24", "fec22")
    ]
    for case, fec, reps in specs:
        if only and case not in only.split(","):
            continue
        new = ["coparticipation", "bipartite_aa"] if fec else ["coparticipation", "cosupport"]
        best = "cofunding" if fec else "aa_total"
        models = ["BM", "BS1", "LR"] if fec else ["M5", "S1", "LR"]
        o = {}
        for mech in ("MCAR", "MNAR-out"):
            rs = [merged(resdir, case, mech, r, fec) for r in range(1, reps + 1)]
            M = {}
            for s in ("random", "matched", "perturb"):
                keys = new + [best] + [m for m in models if m in rs[0][s][0][0]]
                M[s] = {k: float(np.mean([win(r[s], k).mean() for r in rs])) for k in keys}
                spon = [np.array([p[2] for p in r[s]]) for r in rs]
                con = {}
                for x in models:
                    if x not in rs[0][s][0][0]:
                        continue
                    for y in new:
                        vec = [win(r[s], x) - win(r[s], y) for r in rs]
                        con[f"{x} - {y}"] = [
                            float(np.mean([v.mean() for v in vec])),
                            *cluster_boot(vec, spon),
                        ]
                for y in new:
                    vec = [win(r[s], y) - win(r[s], best) for r in rs]
                    con[f"{y} - {best}"] = [
                        float(np.mean([v.mean() for v in vec])),
                        *cluster_boot(vec, spon),
                    ]
                M[s + "_contrasts"] = con
            o[mech] = M
        S[case] = o
        print(case, "done", flush=True)
        json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
