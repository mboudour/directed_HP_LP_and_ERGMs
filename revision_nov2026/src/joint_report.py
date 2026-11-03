"""Compare exact joint footprint scores L_J with factorized L_1g on the same masks."""

import glob
import json
import pickle
import sys

import aggregate as ag
import numpy as np

res_dir, joint_dir, out = sys.argv[1:4]
rows = {}
for f in sorted(glob.glob(f"{joint_dir}/*.pkl")):
    key = f.rsplit("/", 1)[-1][:-4]
    mech, rep = key.rsplit("_", 1)
    J = pickle.load(open(f, "rb"))
    R = pickle.load(open(f"{res_dir}/{key}.pkl", "rb"))
    for model in ["M4c", "M5"]:
        for panel in ["random", "sub"]:
            lj = J[model][panel]
            sizes = [len(x[2][1]) for x in R[panel]]
            pos, neg = [a for a, b in lj], [b for a, b in lj]
            posn = [a / k for a, k in zip(pos, sizes, strict=False)]
            negn = [b / k for b, k in zip(neg, sizes, strict=False)]
            l1g = ag.panel_metric(R[panel], f"{model}_L1g")[0]
            rows.setdefault((mech, model, panel), []).append(
                (ag._ap(pos, neg)[0], ag._ap(posn, negn)[0], l1g)
            )
summary = {}
for (mech, model, panel), v in rows.items():
    v = np.array(v)
    summary[f"{mech}|{model}|{panel}"] = {
        "masks": len(v),
        "LJ": float(v[:, 0].mean()),
        "LJ_per_arc": float(v[:, 1].mean()),
        "L1g": float(v[:, 2].mean()),
        "LJ_minus_L1g": ag.paired(v[:, 0] - v[:, 2]),
        "LJ_per_arc_minus_L1g": ag.paired(v[:, 1] - v[:, 2]),
    }
json.dump(summary, open(out, "w"), indent=1)
print(json.dumps(summary, indent=1))
