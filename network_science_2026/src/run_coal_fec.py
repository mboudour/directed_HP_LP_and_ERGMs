# ruff: noqa: E501
"""Coalition-aware and Adamic--Adar-type scores for the contribution benchmark.

Rebuilds each mask of run_fec (same seeds) and scores the random, party-matched and
head-perturbation pairs with
  * co-participation: mean, over pairs of participants (committee and candidates), of the
    number of training batches containing both;
  * bipartite Adamic--Adar: three-paths c -> j' <- c' -> j weighted by 1 / log(1 + d(c'))
    of the intermediate committee, averaged over the footprint;
  * weighted footprint, to check alignment with the stored run.

Usage: python run_coal_fec.py FEC_DIR DIME CYCLE FEC_RESULTS OUTDIR
"""

import glob
import os
import pickle
import sys

import fec_case as F
import numpy as np
import run_fec as R
from scipy import sparse as sp


def run_split(case, mech, rep):
    m = F.mask(case, mech, rep)
    Y, W, bills = F.training(case, m)
    n = case.C + case.K
    ri, ci, vi = [], [], []
    e = 0
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            for v in [s, *[case.C + h for h in H]]:
                ri.append(e)
                ci.append(v)
                vi.append(np.sqrt(c))
            e += 1
    B = sp.csr_matrix((vi, (ri, ci)), shape=(e, n))
    Cp = (B.T @ B).toarray()
    A = Y.astype(float)
    wc = 1 / np.log1p(np.maximum(A.sum(1), 1))
    AA = (A @ A.T * wc[None, :]) @ A
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    act_c, act_k = Y.sum(1) > 0, Y.sum(0) > 0
    pos = [t for t in held if act_c[t[0]] and all(act_k[h] for h in t[1])]
    lean = R.covariates(case, Y)[0]

    def score(s, H):
        Hl = sorted(H)
        P = [s, *[case.C + h for h in Hl]]
        iu = np.triu_indices(len(P), 1)
        return {
            "coparticipation": float(Cp[np.ix_(P, P)][iu].mean()),
            "bipartite_aa": float(AA[s, Hl].mean()),
            "weighted_footprint": float(W[s, Hl].mean()),
        }

    out = {}
    for kind in ("random", "matched", "perturb"):
        neg = F.negatives(case, pos, Y, mech, rep, kind, lean=lean)
        out[kind] = [
            (score(*p), score(*q)) for p, q in zip(pos, neg, strict=False) if q is not None
        ]
    return out


def main(fec_dir, dime, cycle, resdir, outdir):
    os.makedirs(outdir, exist_ok=True)
    case = F.build_case(fec_dir, dime, int(cycle))
    for f in sorted(glob.glob(f"{resdir}/M*_*.pkl")):
        g = f"{outdir}/{os.path.basename(f)}"
        if os.path.exists(g):
            continue
        mech, rep = os.path.basename(f)[:-4].rsplit("_", 1)
        r = run_split(case, mech, int(rep))
        old = pickle.load(open(f, "rb"))
        for k in r:
            a = [p[i]["weighted_footprint"] for p in r[k] for i in (0, 1)]
            b = [p[i]["weighted_footprint"] for p in old[k] for i in (0, 1)]
            assert len(a) == len(b) and np.allclose(a, b), (f, k)
        pickle.dump(r, open(g, "wb"))
        print(cycle, mech, rep, flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:6])
