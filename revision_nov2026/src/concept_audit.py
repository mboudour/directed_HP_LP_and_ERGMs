"""Cap-first formal-concept audit: concepts of the full projection vs recorded types."""

import json
import sys
import time

import events
import runlib


def audit(name, cT=3, caps=(10, 15)):
    case = runlib.make_case(name)
    out = {}
    for cH in caps:
        t = time.time()
        T = [(s, H) for (s, H) in case.all_types_count if len(H) <= cH]
        ev_arcs = {(case.idx[s], case.idx[h]) for s, H in T for h in H}
        Ts = {(frozenset([case.idx[s]]), frozenset(case.idx[h] for h in H)) for s, H in T}
        C = events.concepts_bitset(case.Yall, cT, cH)
        c_arcs = {(i, j) for Tt, H in C for i in Tt for j in H}
        out[cH] = {
            "types": len(T),
            "concepts": len(C),
            "concept_arcs": len(c_arcs),
            "type_arcs": len(ev_arcs),
            "jaccard": len(c_arcs & ev_arcs) / max(1, len(c_arcs | ev_arcs)),
            "exact": len(C & Ts),
            "seconds": round(time.time() - t, 1),
        }
        print(name, cH, out[cH], flush=True)
    return out


if __name__ == "__main__":
    res = {n: audit(n) for n in sys.argv[2:]}
    json.dump(res, open(sys.argv[1], "w"), indent=1)
