# ruff: noqa: E501
"""Decompose the gain of the political covariates on the party-matched sets (S0 plus one covariate).

For each mask of a case, fits S0, S0+party, S0+state, S0+ideology and S1 by exact MLE
(structural zeros as in run_v3) and reports concordance on the party-matched sets,
separately for bipartisan and single-party hyperarcs.

Usage: python decomp_v3.py CASE OUT_JSON
"""

import json
import sys

import benchmark
import ergm
import numpy as np
import p1
import runlib
from aggregate import paired
from run_v2 import matched_negatives
from run_v3 import overlap_matrix

BASE = ["edges", "mutual", "sender", "receiver"]
MODELS = {
    "S0": BASE,
    "S0+party": BASE + ["nodematch_party"],
    "S0+state": BASE + ["nodematch_state"],
    "S0+ideology": BASE + ["absdiff_nominate"],
    "S1": ergm.LADDER["S1"],
}


def main(name, out):
    case = runlib.make_case(name)
    allowed = overlap_matrix(case)
    cov = case.cov
    res = {}
    for mech in ["MCAR", "MNAR-out"]:
        per = {k: {"bipartisan": [], "single_party": []} for k in MODELS}
        for rep in range(1, 31):
            m, _ = case.mask(mech, rep)
            n = case.n
            Y = np.zeros((n, n), np.int8)
            for (s, H), mm in zip(case.types, m, strict=False):
                if not mm:
                    Y[s, list(H)] = 1
            R = benchmark.reach2(Y)
            held = [t for t, mm in zip(case.types, m, strict=False) if mm]
            pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
            neg, _ = matched_negatives(case, pos, R, mech, rep)
            bip = np.array(
                [
                    any(cov["caucus"][h] != cov["caucus"][s] for h in H)
                    for (s, H), q in zip(pos, neg, strict=False)
                    if q is not None
                ]
            )
            pairs = [(p, q) for p, q in zip(pos, neg, strict=False) if q is not None]
            for k, terms in MODELS.items():
                th, _ = p1.fit(Y, terms, cov, allowed=allowed)
                P, _ = ergm.conditional_probs(Y, terms, th, cov)

                def sc(s, H, P=P):
                    return float(np.mean(np.log(np.clip(P[s, sorted(H)], 1e-300, 1))))

                w = np.array([(sc(*a) > sc(*b)) + 0.5 * (sc(*a) == sc(*b)) for a, b in pairs])
                per[k]["bipartisan"].append(float(w[bip].mean()))
                per[k]["single_party"].append(float(w[~bip].mean()))
            print(name, mech, rep, flush=True)
        out_m = {}
        for cl in ["bipartisan", "single_party"]:
            base = np.array(per["S0"][cl])
            out_m[cl] = {
                k: {
                    "mean": float(np.mean(per[k][cl])),
                    "gain_over_S0": paired(np.array(per[k][cl]) - base),
                }
                for k in MODELS
            }
        res[mech] = out_m
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
