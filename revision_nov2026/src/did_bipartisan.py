# ruff: noqa: E501
"""Sponsor-bootstrap intervals for the difference between bipartisan and single-party hyperarcs in
the gain from the political covariates (M5 - M4c, S1 - S0) on the party-matched sets.

Each replicate draws sponsors with replacement (multinomial weights), shared by all masks;
within each mask the class means are weighted by the sponsor weights; the replicate value is the
mean over masks of (bipartisan gain - single-party gain).

Usage: python did_bipartisan.py RESULTS_DIR OUT_JSON
"""

import json
import pickle
import sys

import numpy as np
from summary_v3 import win


def main(resdir, out, B=2000, seed=1):
    S = {}
    for case in ("s118", "s117", "s116", "h118"):
        for mech in ("MCAR", "MNAR-out"):
            rs = [
                pickle.load(open(f"{resdir}/v3_{case}/{mech}_{r:02d}.pkl", "rb"))["matched"]
                for r in range(1, 31)
            ]
            sp = [np.array([p[2]["sponsor"] for p in r]) for r in rs]
            bi = [np.array([p[2]["other"] >= 1 for p in r]) for r in rs]
            allsp = np.unique(np.concatenate(sp))
            idx = {v: i for i, v in enumerate(allsp)}
            spi = [np.array([idx[v] for v in s]) for s in sp]
            rng = np.random.default_rng(seed)
            Wt = rng.multinomial(len(allsp), np.ones(len(allsp)) / len(allsp), size=B).astype(float)
            o = {}
            for x, y in (("M5", "M4c"), ("S1", "S0")):
                d = [win(r, x) - win(r, y) for r in rs]
                est = float(
                    np.mean([dd[b].mean() - dd[~b].mean() for dd, b in zip(d, bi, strict=True)])
                )
                reps = np.zeros(B)
                for dd, b, si in zip(d, bi, spi, strict=True):
                    w = Wt[:, si]
                    wb, wn = w * b, w * (~b)
                    reps += (wb @ dd) / np.maximum(wb.sum(1), 1e-12) - (wn @ dd) / np.maximum(
                        wn.sum(1), 1e-12
                    )
                reps /= len(rs)
                o[f"{x} - {y}"] = [
                    est,
                    float(np.percentile(reps, 2.5)),
                    float(np.percentile(reps, 97.5)),
                ]
            S[f"{case}_{mech}"] = o
            print(case, mech, {k: [round(v, 3) for v in vv] for k, vv in o.items()}, flush=True)
    json.dump(S, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
