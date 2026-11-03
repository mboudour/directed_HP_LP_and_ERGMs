"""Second benchmark run: exact p1 MLE, party-matched candidates and hypergraph baselines.

For each of the 60 masks of a case this script fits
  * MPLE: M4c, M5, M6, S0, S1
  * exact MLE (p1.fit): S0, S1  (keys S0mle, S1mle)
and scores every candidate with the local scores of benchmark.LOCAL plus two
baselines that use the observed hypergraph:
  * sponsor_bills: number of observed records whose tail is the candidate initiator
  * observed_fraction: share of the candidate footprint present in the training 2-section.
Candidate sets: random (published sampler), party-matched random (same initiator
caucus and same caucus composition of the head), substitution, role assignment.
Per-pair scores are stored so that pooled and within-pair metrics can be computed.

Usage: python run_v2.py CASE OUTDIR [REPS]
"""

import collections
import os
import pickle
import random
import sys
import time

import benchmark
import ergm
import numpy as np
import p1
import runlib

MPLE_MODELS = ["M4c", "M5", "M6", "S0", "S1"]
MLE_MODELS = ["S0", "S1"]


def matched_negatives(case, positives, R, mech, replicate):
    """Random candidates with the initiator's caucus and the head's caucus composition fixed."""
    rnd = random.Random(case.neg_seed + 7_919 * replicate + (0 if mech == "MCAR" else 3_001) + 1)
    cau = case.cov["caucus"]
    groups = collections.defaultdict(list)
    for i in range(case.n):
        groups[int(cau[i])].append(i)
    used, out, audit = set(), [], collections.Counter()
    for s, H in positives:
        comp = collections.Counter(int(cau[h]) for h in H)
        dates = case.type_dates[(s, H)]
        acc = None
        for _ in range(100_000):
            audit["attempts"] += 1
            s2 = rnd.choice(groups[int(cau[s])])
            H2 = []
            ok = True
            for c, k in sorted(comp.items()):
                pool = [x for x in groups[c] if x != s2]
                if len(pool) < k:
                    ok = False
                    break
                H2 += rnd.sample(pool, k)
            if not ok:
                continue
            key = (s2, frozenset(H2))
            if key in case.complete or key in used:
                continue
            pick = [s2] + H2
            if not R[np.ix_(pick, pick)].all():
                continue
            if not case.serve_ok(pick, dates):
                continue
            used.add(key)
            acc = key
            break
        if acc is None:
            audit["failed"] += 1
        out.append(acc)
    return out, audit


def run_split(case, mech, replicate):
    m, seed = case.mask(mech, replicate)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    bills = np.zeros(n)
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            bills[s] += c
    R = benchmark.reach2(Y)
    held = [t for t, mm in zip(case.types, m, strict=False) if mm]
    pos = [t for t in held if R[np.ix_(list(t[1] | {t[0]}), list(t[1] | {t[0]}))].all()]
    cov = case.cov
    info = {
        "case": case.name,
        "mech": mech,
        "replicate": replicate,
        "heldout": len(held),
        "evaluated": len(pos),
        "zero_outdegree": int((Y.sum(1) == 0).sum()),
        "zero_indegree": int((Y.sum(0) == 0).sum()),
    }
    Lm = benchmark.local_matrices(Y, cov)
    Lm["sponsor_bills"] = np.repeat(bills[:, None], n, 1)
    Lm["observed_fraction"] = Y.astype(float)
    local = benchmark.LOCAL + ["sponsor_bills", "observed_fraction"]
    P, theta, mle_info = {}, {}, {}
    for name in MPLE_MODELS:
        terms = ergm.LADDER[name]
        X, yv, _ = ergm.design(Y, terms, cov)
        th, _ = ergm.mple(X, yv)
        theta[name] = th
        P[name], _ = ergm.conditional_probs(Y, terms, th, cov)
    for name in MLE_MODELS:
        terms = ergm.LADDER[name]
        th, inf = p1.fit(Y, terms, cov)
        inf.pop("names")
        mle_info[name] = inf
        theta[name + "mle"] = th
        P[name + "mle"], _ = ergm.conditional_probs(Y, terms, th, cov)
    info["mle"] = mle_info

    def score(s, H):
        Hl = sorted(H)
        out = {k: float(Lm[k][s, Hl].mean()) for k in local}
        for name, Pm in P.items():
            p = np.clip(Pm[s, Hl], 1e-300, 1)
            out[name] = float(np.exp(np.log(p).mean()))
        return out

    def meta(s, H):
        other = sum(int(cov["caucus"][h] != cov["caucus"][s]) for h in H)
        return {"size": len(H), "other": other}

    negs, _ = case.random_negatives(pos, R, mech, replicate)
    mneg, maudit = matched_negatives(case, pos, R, mech, replicate)
    info["matched_failed"] = maudit["failed"]
    subs = dict(benchmark.substitution_pairs(case, pos, R, mech, replicate))
    rand, matched, sub, role = [], [], [], []
    for (s, H), q, qm in zip(pos, negs, mneg, strict=False):
        sp_ = score(s, H)
        mt = meta(s, H)
        if q is not None:
            rand.append((sp_, score(*q), mt))
        if qm is not None:
            matched.append((sp_, score(*qm), mt))
        if (s, H) in subs:
            sub.append((sp_, score(*subs[(s, H)]), mt))
        Pset = sorted(H | {s})
        role.append(([score(x, frozenset(Pset) - {x}) for x in Pset], Pset.index(s), mt))
    th_out = {}
    for k, v in theta.items():
        names = ergm.expand_terms(ergm.LADDER[k.replace("mle", "")], n)
        th_out[k] = {
            nm: float(x)
            for nm, x in zip(names, v, strict=False)
            if not nm.startswith(("sender_", "receiver_"))
        }
    return {
        "info": info,
        "theta": th_out,
        "random": rand,
        "matched": matched,
        "sub": sub,
        "role": role,
    }


def main(name, outdir, reps=30):
    os.makedirs(outdir, exist_ok=True)
    case = runlib.make_case(name)
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = run_split(case, mech, rep)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30)
