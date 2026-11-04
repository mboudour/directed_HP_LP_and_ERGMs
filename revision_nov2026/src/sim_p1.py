# ruff: noqa: E501
"""Exact simulation from the MLE of the dyad-independent models (S0, S1, SI) on the complete 2-sections.

Each unordered dyad is drawn independently from its four-state distribution at the MLE
(with structural zeros), so no MCMC is needed. Reports observed values and simulated
means and central 95% ranges of statistics outside the models' sufficient statistics:
transitive and cyclic triples, mean edgewise shared partners (two-paths), and the share
of arcs with at least one two-path partner, plus arcs and mutual dyads as checks.

Usage: python sim_p1.py OUT_JSON [NSIM]
"""

import json
import sys

import ergm
import numpy as np
import p1
import runlib
from run_v3 import MLE_MODELS, overlap_matrix

CASES = ["s118", "s117", "s116", "h118"]


def stats(A):
    A = A.astype(float)
    OI = A @ A
    tt = float((A * OI).sum())  # transitive triples i->k->j with i->j
    ct = float((A.T * OI).sum() / 3)  # cyclic triples
    esp = OI[A > 0]
    return {
        "arcs": float(A.sum()),
        "mutual": float((A * A.T).sum() / 2),
        "ttriple": tt,
        "ctriple": ct,
        "mean_esp_otp": float(esp.mean()),
        "share_arcs_esp_ge1": float((esp >= 1).mean()),
    }


def main(out, nsim=500):
    rng = np.random.default_rng(20261104)
    res = {}
    for c in CASES:
        case = runlib.make_case(c)
        Y = case.Ycap.astype(np.int8)
        n = case.n
        allowed = overlap_matrix(case)
        obs = stats(Y)
        res[c] = {"observed": obs}
        for name in ["S0", "S1", "SI"]:
            terms = MLE_MODELS[name]
            th, _ = p1.fit(Y, terms, case.cov, allowed=allowed)
            _, iu, ju, S1, S2, S3 = p1._dyad_design(n, terms, case.cov, allowed)
            e = np.stack([np.zeros(len(iu)), S1 @ th, S2 @ th, S3 @ th], 1)
            pr = np.exp(e - np.logaddexp.reduce(e, 1)[:, None])
            cum = pr.cumsum(1)
            sims = []
            for _ in range(nsim):
                u = rng.random(len(iu))[:, None]
                st = (u > cum).sum(1)
                A = np.zeros((n, n), np.int8)
                A[iu[(st == 1) | (st == 3)], ju[(st == 1) | (st == 3)]] = 1
                A[ju[(st == 2) | (st == 3)], iu[(st == 2) | (st == 3)]] = 1
                sims.append(stats(A))
            res[c][name] = {
                k: [
                    float(np.mean([s[k] for s in sims])),
                    float(np.percentile([s[k] for s in sims], 2.5)),
                    float(np.percentile([s[k] for s in sims], 97.5)),
                ]
                for k in obs
            }
            print(
                c,
                name,
                {k: (round(obs[k], 3), [round(x, 3) for x in v]) for k, v in res[c][name].items()},
                flush=True,
            )
    json.dump(res, open(out, "w"), indent=1)
    _ = ergm


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 500)
