# ruff: noqa: E501
"""Robustness: hyperarcs defined by committee and seven-day window instead of committee and date.

Usage: python run_fec_week.py FEC_DIR DIME CYCLE OUTDIR [REPS] [WINDOW_DAYS]
"""

import os
import pickle
import sys
import time

import fec_case as F
import run_fec as R


def main(fec_dir, dime, cycle, outdir, reps=10, window=7):
    os.makedirs(outdir, exist_ok=True)
    case = F.build_case(fec_dir, dime, int(cycle), window_days=window)
    pickle.dump(
        {"accounting": case.accounting, "C": case.C, "K": case.K}, open(f"{outdir}/meta.pkl", "wb")
    )
    print(case.accounting, flush=True)
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
    main(a[1], a[2], a[3], a[4], int(a[5]) if len(a) > 5 else 10, int(a[6]) if len(a) > 6 else 7)
