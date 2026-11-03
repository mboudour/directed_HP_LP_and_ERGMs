"""Run all 60 splits (30 MCAR, 30 MNAR-out) for one case; one pickle per split."""

import os
import pickle
import sys
import time

import benchmark
import runlib

MODELS = ["M0", "M1", "M2", "M3", "M4", "M4c", "M4c_nomut", "M5", "M6"]


def main(name, outdir, reps=30, models=None):
    models = models or MODELS
    os.makedirs(outdir, exist_ok=True)
    if name.endswith("uncap"):
        case = runlib.make_case(name[:-5])
        case.train_uncapped = True
        case.name = name
    elif name.endswith("cap3"):
        case = runlib.make_case(name[:-4], head_cap=3)
        case.name = name
    else:
        case = runlib.make_case(name)
    meta = {
        "n": case.n,
        "types": len(case.types),
        "records": sum(case.counts),
        "valid_events": len(case.events),
        "all_types": len(case.all_types_count),
        "dropped": dict(case.dropped),
        "arcs_cap": int(case.Ycap.sum()),
        "arcs_all": int(case.Yall.sum()),
        "nominate_missing": [b for b in case.nodes if b not in case.nominate_source],
        "nominate_fallback": {b: s for b, s in case.nominate_source.items()},
        "party_counts": {
            p: int((case.cov["party"] == k).sum())
            for k, p in enumerate(sorted({a["party"] for a in case.U.values()}))
        },
        "majority": int(case.cov["majority"].sum()),
    }
    pickle.dump(meta, open(f"{outdir}/meta.pkl", "wb"))
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = benchmark.run_split(case, mech, rep, models, with_role=True)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    main(
        sys.argv[1],
        sys.argv[2],
        reps=int(sys.argv[4]) if len(sys.argv) > 4 else 30,
        models=sys.argv[3].split(",") if len(sys.argv) > 3 else None,
    )
