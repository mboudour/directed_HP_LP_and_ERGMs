# ruff: noqa: E501
"""Robustness: committee ideology from DIME contributor CFscores (matched by name) instead of
the mean CFscore of the committee's training recipients; committees without a match keep the
training-based value. Everything else as in run_fec.py.

Usage: python run_fec_dime.py FEC_DIR DIME_RECIPIENTS CYCLE COMM_CF_NPY OUTDIR [REPS]
"""

import os
import pickle
import sys
import time

import fec_case as F
import numpy as np
import run_fec as R

_orig = R.covariates


def main(fec_dir, dime, cycle, cf_npy, outdir, reps=10):
    os.makedirs(outdir, exist_ok=True)
    case = F.build_case(fec_dir, dime, int(cycle))
    ext = np.load(cf_npy)

    def covariates(case_, Y):
        lean, ideo, align, dist = _orig(case_, Y)
        ideo = np.where(np.isfinite(ext), ext, ideo)
        dist = np.abs(ideo[:, None] - case_.cand_cf[None, :])
        return lean, ideo, align, dist

    R.covariates = covariates
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = R.run_split(case, mech, rep)
            pickle.dump(r, open(f, "wb"))
            print(cycle, mech, rep, r["info"]["tau_hat"], round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4], a[5], int(a[6]) if len(a) > 6 else 10)
