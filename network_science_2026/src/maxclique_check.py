# ruff: noqa: E501
"""Undirected counterpart of the concept check: is an eligible hyperedge (sponsor and original
co-sponsors) a maximal clique of the undirected 2-section (clique graph) of all records?

Usage: python maxclique_check.py OUT_JSON
"""

import json
import sys

import numpy as np
import runlib


def main(out):
    res = {}
    for name in ("s118", "s117", "s116", "h118"):
        case = runlib.make_case(name)
        n = case.n
        A = np.zeros((n, n), bool)
        for (sb, Hb), _ in case.all_types_count.items():
            P = [case.idx[sb], *[case.idx[h] for h in Hb]]
            A[np.ix_(P, P)] = True
        np.fill_diagonal(A, False)
        maximal, common, tri = [], [], 0
        for s, H in case.types:
            P = sorted({s, *H})
            cn = np.nonzero(A[P].all(0))[0]
            cn = [v for v in cn if v not in P]
            maximal.append(len(cn) == 0)
            common.append(len(cn))
        iu = np.triu_indices(n, 1)
        Af = A.astype(float)
        tri = int(np.trace(Af @ Af @ Af) // 6)
        res[name] = {
            "eligible": len(case.types),
            "share_maximal_clique": float(np.mean(maximal)),
            "mean_common_neighbours": float(np.mean(common)),
            "median_common_neighbours": float(np.median(common)),
            "density": float(A[iu].mean()),
            "triangles": tri,
        }
        print(name, res[name], flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
