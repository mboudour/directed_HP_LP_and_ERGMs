# ruff: noqa: E501
"""Profile pseudolikelihood of BM beyond the grid, and concordance at the larger decays, for a few masks."""

import json

import fec_case as F
import numpy as np
import run_fec as R
from summary_v3 import win

out = {}
for cyc, fdir in [(2024, "../../fec24"), (2022, "../../fec22")]:
    case = F.build_case(fdir, "../../dime/recipients.csv.gz", cyc)
    for mech in ["MCAR", "MNAR-out"]:
        for rep in (1, 2):
            m = F.mask(case, mech, rep)
            Y, W, bills = F.training(case, m)
            held = [t for t, mm in zip(case.types, m, strict=False) if mm]
            act_c, act_k = Y.sum(1) > 0, Y.sum(0) > 0
            pos = [t for t in held if act_c[t[0]] and all(act_k[h] for h in t[1])]
            lean, ideo, align, dist = R.covariates(case, Y)
            res = {}
            negs = {
                k: F.negatives(case, pos, Y, mech, rep, k, lean=lean)
                for k in ("random", "matched", "perturb")
            }
            for tau in [3.0, 4.0, 5.0, 6.0, 8.0]:
                P, th, pl = R.fit_bm(case, Y, tau, align, dist)

                def sc(s, H, P=P):
                    return float(np.exp(np.log(np.clip(P[s, sorted(H)], 1e-300, 1)).mean()))

                conc = {}
                for k, neg in negs.items():
                    pr = [
                        ({"BM": sc(*p)}, {"BM": sc(*q)})
                        for p, q in zip(pos, neg, strict=False)
                        if q is not None
                    ]
                    conc[k] = float(win(pr, "BM").mean())
                res[tau] = {"pl": pl, **conc}
                print(
                    cyc,
                    mech,
                    rep,
                    tau,
                    round(pl, 1),
                    {k: round(v, 3) for k, v in conc.items()},
                    flush=True,
                )
            out[f"{cyc}_{mech}_{rep}"] = res
json.dump(out, open("../../results/fec_tau_check.json", "w"), indent=1)
