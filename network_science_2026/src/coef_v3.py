# ruff: noqa: E501
"""Coefficients on the complete 2-section of each case (third run).

M4c and M5 by MPLE with the decay selected by profile pseudolikelihood of M5;
S0, S1 and SI by exact (ridge-penalized) MLE with structural zeros for dyads of
legislators whose service did not overlap; S0 and S1 also by MPLE.

Usage: python coef_v3.py OUT_JSON
"""

import json
import sys

import ergm
import numpy as np
import p1
import runlib
from run_v3 import MLE_MODELS, TAU_GRID, fit_mple, overlap_matrix

CASES = ["s118", "s117", "s116", "h118"]


def main(out):
    res = {}
    for c in CASES:
        case = runlib.make_case(c)
        Y = case.Ycap.astype(np.int8)
        n = case.n
        r = {"n": n, "arcs": int(Y.sum()), "mutual": int((Y * Y.T).sum() // 2)}
        allowed = overlap_matrix(case)
        prof = {}
        for tau in TAU_GRID:
            ergm.DECAY = tau
            prof[tau] = fit_mple(Y, ergm.LADDER["M5"], case.cov)[1]
        tau_hat = max(prof, key=prof.get)
        r["tau_profile"] = prof
        r["tau_hat"] = tau_hat
        for name in ["M4c", "M5", "S0", "S1", "SI"]:
            ergm.DECAY = tau_hat if name.startswith("M") else 0.5
            terms = MLE_MODELS.get(name, ergm.LADDER.get(name))
            names = ergm.expand_terms(terms, n)
            X, yv, _ = ergm.design(Y, terms, case.cov)
            th, _ = ergm.mple(X, yv)
            r[name + "_mple"] = {
                t: float(v)
                for t, v in zip(names, th, strict=False)
                if not t.startswith(("sender_", "receiver_"))
            }
            if name.startswith("S"):
                if name == "SI":
                    r.pop(name + "_mple", None)
                thm, info = p1.fit(Y, terms, case.cov, allowed=allowed)
                info.pop("names")
                r[name + "_mle"] = {
                    t: float(v)
                    for t, v in zip(names, thm, strict=False)
                    if not t.startswith(("sender_", "receiver_"))
                }
                r[name + "_mle_info"] = info
                if name == "SI":
                    continue
                se = thm[[k for k, t in enumerate(names) if t.startswith("sender_")]]
                re_ = thm[[k for k, t in enumerate(names) if t.startswith("receiver_")]]
                r[name + "_mle_actor_sd"] = {
                    "sender": float(np.std(se[se > -8])),
                    "receiver": float(np.std(re_[re_ > -8])),
                }
                conn_out = (Y.sum(1) > 0)[1:]
                conn_in = (Y.sum(0) > 0)[1:]
                r[name + "_max_abs_effect_connected"] = float(
                    max(np.abs(se[conn_out]).max(), np.abs(re_[conn_in]).max())
                )
                # sender effects (node 0 is the baseline, effect 0) regressed on actor attributes
                sender = np.r_[0.0, se]
                keep = Y.sum(1) > 0
                X = np.column_stack(
                    [
                        np.ones(n),
                        case.cov["majority"],
                        case.cov["seniority"],
                        (case.cov["caucus"] == 1).astype(float),
                        np.abs(case.cov["nominate"]),
                    ]
                )[keep]
                yv_ = sender[keep]
                beta, *_ = np.linalg.lstsq(X, yv_, rcond=None)
                resid = yv_ - X @ beta
                r2 = 1 - resid.var() / yv_.var()
                X2 = X[:, :3]
                b2, *_ = np.linalg.lstsq(X2, yv_, rcond=None)
                r2_inst = 1 - (yv_ - X2 @ b2).var() / yv_.var()
                lbills = np.log1p(
                    np.array(
                        [
                            sum(
                                c
                                for (s_, H), c in zip(case.types, case.counts, strict=False)
                                if s_ == i
                            )
                            for i in range(n)
                        ]
                    )
                )[keep]
                r[name + "_sender_regression"] = {
                    "coef_const_majority_seniority_republican_absnominate": beta.tolist(),
                    "r2_all": float(r2),
                    "r2_majority_seniority": float(r2_inst),
                    "corr_log_bills": float(np.corrcoef(yv_, lbills)[0, 1]),
                    "actors": int(keep.sum()),
                }
        res[c] = r
        print(c, flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
