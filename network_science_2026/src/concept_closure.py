"""Uncapped comparison of each recorded hyperarc with the formal concepts it generates.

For a hyperarc ({s}, H) of the 2-section Y of all recorded hyperarcs:
  * head-generated concept: (H^down, H^down^up), the smallest concept whose head contains H;
  * tail-generated concept: ({s}^up^down, {s}^up), the concept whose head is N^+(s).
Reported per case: share of hyperarcs equal to their head-generated concept,
mean tail size of that concept, mean ratio |H| / |H^down^up|, mean Jaccard of
footprints, and mean ratio |H| / |N^+(s)|.

Usage: python concept_closure.py OUT_JSON
"""

import json
import sys

import numpy as np
import runlib

CASES = ["s118", "s117", "s116", "h118"]


def main(out):
    res = {}
    for c in CASES:
        case = runlib.make_case(c)
        Y = case.Yall.astype(bool)
        rows = []
        for s, H in case.types:
            Hl = sorted(H)
            Tst = np.nonzero(Y[:, Hl].all(1))[0]  # H^down, contains s
            Hst = np.nonzero(Y[Tst].all(0))[0]  # H^down^up, contains H
            nplus = int(Y[s].sum())
            fp = {(s, h) for h in Hl}
            fc = {(i, j) for i in Tst for j in Hst}
            rows.append(
                (
                    len(Tst) == 1 and len(Hst) == len(Hl),
                    len(Tst),
                    len(Hl) / max(1, len(Hst)),
                    len(fp & fc) / len(fp | fc),
                    len(Hl) / nplus,
                    len(Hl) == nplus,
                )
            )
        a = np.array(rows, float)
        res[c] = {
            "hyperarcs": len(rows),
            "share_equal_head_concept": float(a[:, 0].mean()),
            "mean_tail_size_head_concept": float(a[:, 1].mean()),
            "median_tail_size_head_concept": float(np.median(a[:, 1])),
            "mean_head_ratio": float(a[:, 2].mean()),
            "mean_footprint_jaccard": float(a[:, 3].mean()),
            "median_footprint_jaccard": float(np.median(a[:, 3])),
            "mean_head_over_outneighbourhood": float(a[:, 4].mean()),
            "share_head_equals_outneighbourhood": float(a[:, 5].mean()),
        }
        print(c, res[c], flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
