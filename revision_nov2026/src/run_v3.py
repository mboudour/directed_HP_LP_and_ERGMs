# ruff: noqa: E501
"""Third benchmark run: estimated decay, structural zeros, head perturbation, survival strata.

Per mask of a case this script fits
  * degree-term models M4c, M5, M6 by MPLE with the decay tau selected by
    profile pseudolikelihood of M5 on the training 2-section over TAU_GRID
    (keys M4c, M5, M6), and M5 with tau = 0.5 (key M5_t05);
  * by exact (ridge-penalized) MLE with structural zeros for dyads of legislators
    whose service did not overlap: S0, S1, and SI (receiver effects, initiator
    majority-caucus membership and seniority, covariates; no sender effects);
and scores candidates with the local scores, the initiator bill count, the
observed footprint share and the weighted footprint (mean number of observed
records containing each arc).
Candidate sets: random, party-matched, head perturbation (tail fixed, one head
member replaced), substitution, role assignment. Each pair stores whether the
footprints of both candidates survive in the training 2-section and the sponsor.

Usage: python run_v3.py CASE OUTDIR [REPS]
"""

import datetime as dt
import os
import pickle
import random
import sys
import time

import actors
import benchmark
import ergm
import numpy as np
import p1
import runlib
from run_v2 import matched_negatives

TAU_GRID = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
MLE_MODELS = {
    "S0": ergm.LADDER["S0"],
    "S1": ergm.LADDER["S1"],
    "SI": ["edges", "mutual", "receiver", "nodeocov_majority", "nodeocov_seniority"]
    + ["nodematch_party", "nodematch_state", "absdiff_nominate"],
}


def overlap_matrix(case):
    c0, c1 = map(dt.date.fromisoformat, actors.CONGRESS_DATES[case.congress])
    n = case.n
    iv = []
    for i in range(n):
        iv.append([(max(s, c0), min(e, c1)) for s, e in case.terms.get(i, ()) if s < c1 and e > c0])
    A = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i + 1, n):
            ok = any(s1 < e2 and s2 < e1 for s1, e1 in iv[i] for s2, e2 in iv[j])
            A[i, j] = A[j, i] = ok
    return A


def perturb_negatives(case, positives, R, mech, replicate):
    """Tail fixed; one head member replaced by a non-member (same constraints as random sets)."""
    rnd = random.Random(case.neg_seed + 4_421 * replicate + (0 if mech == "MCAR" else 2_003) + 7)
    used, out = set(), []
    for s, H in positives:
        dates = case.type_dates[(s, H)]
        outside = [v for v in range(case.n) if v != s and v not in H]
        acc = None
        for _ in range(20_000):
            h = rnd.choice(sorted(H))
            j = rnd.choice(outside)
            H2 = frozenset((H - {h}) | {j})
            key = (s, H2)
            if key in case.complete or key in used:
                continue
            pick = [s] + sorted(H2)
            if not R[np.ix_(pick, pick)].all():
                continue
            if not case.serve_ok(pick, dates):
                continue
            used.add(key)
            acc = key
            break
        out.append(acc)
    return out


def fit_mple(Y, terms, cov):
    X, yv, _ = ergm.design(Y, terms, cov)
    th, _ = ergm.mple(X, yv)
    eta = X @ th
    return th, float((yv * eta - np.logaddexp(0, eta)).sum())


def run_split(case, mech, replicate, allowed):
    m, seed = case.mask(mech, replicate)
    n = case.n
    Y = np.zeros((n, n), np.int8)
    W = np.zeros((n, n))
    bills = np.zeros(n)
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Y[s, list(H)] = 1
            W[s, list(H)] += c
            bills[s] += c
    if getattr(case, "train_uncapped", False):
        noncap = set(case.noncap)
        for (sb, Hb), c in case.all_types_count.items():
            if (case.idx[sb], frozenset(case.idx[h] for h in Hb)) in noncap:
                s, H = case.idx[sb], [case.idx[h] for h in Hb]
                Y[s, H] = 1
                W[s, H] += c
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
    }
    Lm = benchmark.local_matrices(Y, cov)
    Lm["sponsor_bills"] = np.repeat(bills[:, None], n, 1)
    Lm["observed_fraction"] = Y.astype(float)
    Lm["weighted_footprint"] = W
    local = benchmark.LOCAL + ["sponsor_bills", "observed_fraction", "weighted_footprint"]
    P, theta = {}, {}
    # decay selection by profile pseudolikelihood of M5
    prof = {}
    for tau in TAU_GRID:
        ergm.DECAY = tau
        _, pl = fit_mple(Y, ergm.LADDER["M5"], cov)
        prof[tau] = pl
    tau_hat = max(prof, key=prof.get)
    info["tau_profile"] = prof
    info["tau_hat"] = tau_hat
    for name, tau in [("M4c", tau_hat), ("M5", tau_hat), ("M6", tau_hat), ("M5_t05", 0.5)]:
        ergm.DECAY = tau
        terms = ergm.LADDER[name.replace("_t05", "")]
        th, _ = fit_mple(Y, terms, cov)
        theta[name] = (terms, th)
        P[name], _ = ergm.conditional_probs(Y, terms, th, cov)
    ergm.DECAY = 0.5
    mle_info = {}
    for name, terms in MLE_MODELS.items():
        th, inf = p1.fit(Y, terms, cov, allowed=allowed)
        inf.pop("names")
        mle_info[name] = inf
        theta[name] = (terms, th)
        P[name], _ = ergm.conditional_probs(Y, terms, th, cov)
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
        return {
            "size": len(H),
            "other": other,
            "sponsor": int(s),
            "surv": bool(Y[s, sorted(H)].all()),
        }

    def surv(q):
        return bool(Y[q[0], sorted(q[1])].all())

    negs, _ = case.random_negatives(pos, R, mech, replicate)
    mneg, _ = matched_negatives(case, pos, R, mech, replicate)
    pneg = perturb_negatives(case, pos, R, mech, replicate)
    subs = dict(benchmark.substitution_pairs(case, pos, R, mech, replicate))
    sets = {"random": [], "matched": [], "perturb": [], "sub": []}
    role = []
    for k, (s, H) in enumerate(pos):
        sp_ = score(s, H)
        mt = meta(s, H)
        for name, q in [
            ("random", negs[k]),
            ("matched", mneg[k]),
            ("perturb", pneg[k]),
            ("sub", subs.get((s, H))),
        ]:
            if q is not None:
                sets[name].append((sp_, score(*q), dict(mt, neg_surv=surv(q))))
        Pset = sorted(H | {s})
        cands = [score(x, frozenset(Pset) - {x}) for x in Pset]
        role.append((cands, Pset.index(s), dict(mt, bills=[float(bills[x]) for x in Pset])))
    th_out = {}
    for k, (terms, v) in theta.items():
        names = ergm.expand_terms(terms, n)
        th_out[k] = {
            nm: float(x)
            for nm, x in zip(names, v, strict=False)
            if not nm.startswith(("sender_", "receiver_"))
        }
    return {"info": info, "theta": th_out, **sets, "role": role}


def main(name, outdir, reps=30):
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
    allowed = overlap_matrix(case)
    pickle.dump(
        {"structural_zero_dyads": int(((~allowed).sum() - len(allowed)) // 2)},
        open(f"{outdir}/meta.pkl", "wb"),
    )
    for mech in ["MCAR", "MNAR-out"]:
        for rep in range(1, reps + 1):
            f = f"{outdir}/{mech}_{rep:02d}.pkl"
            if os.path.exists(f):
                continue
            t = time.time()
            r = run_split(case, mech, rep, allowed)
            pickle.dump(r, open(f, "wb"))
            print(name, mech, rep, r["info"]["tau_hat"], round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30)
