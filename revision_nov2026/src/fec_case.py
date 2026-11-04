# ruff: noqa: E501
"""FEC committee-to-candidate contributions as a bipartite directed hypergraph.

A hyperarc is the set of House and Senate candidates to whom one committee made
direct contributions (transaction type 24K, positive amount, not a memo entry) on
one date: tail {committee}, head = candidates. The 2-section is the bipartite
committee -> candidate network.

Case construction (per two-year cycle):
  * candidates: House (H) and Senate (S) candidates in the candidate master file,
    receiving from at least MIN_DONORS distinct committees in the cycle;
  * committees: at least MIN_BATCHES eligible hyperarcs in the cycle;
  * eligible hyperarcs: all head members kept and 1 <= |H| <= HEAD_LIMIT.
Masks withhold whole hyperarcs (MCAR, or MNAR-out by committee activity), as in the
co-sponsorship benchmark.

Usage (module): case = build_case(fec_dir, dime_path, cycle)
"""

import collections
import datetime
import random

import numpy as np
import pandas as pd

HEAD_LIMIT = 10
MIN_DONORS = 5
MIN_BATCHES = 10


class FECCase:
    pass


def _period(dte, window_days):
    if not window_days:
        return dte
    try:
        d = datetime.date(int(dte[4:8]), int(dte[0:2]), int(dte[2:4]))
    except ValueError:
        return dte
    return d.toordinal() // window_days


def build_case(
    fec_dir, dime_path, cycle, min_donors=MIN_DONORS, min_batches=MIN_BATCHES, window_days=None
):
    cand = {}
    for line in open(f"{fec_dir}/cn.txt", encoding="latin-1"):
        f = line.rstrip("\n").split("|")
        if f[5] in ("H", "S"):
            cand[f[0]] = {"party": f[2], "state": f[4], "office": f[5], "ici": f[7]}
    comm = {}
    for line in open(f"{fec_dir}/cm.txt", encoding="latin-1"):
        f = line.rstrip("\n").split("|")
        comm[f[0]] = {"state": f[6], "type": f[9], "org": f[12], "dsgn": f[8]}
    batches = collections.defaultdict(set)
    donors = collections.defaultdict(set)
    nrec = 0
    for line in open(f"{fec_dir}/itpas2.txt", encoding="latin-1"):
        f = line.rstrip("\n").split("|")
        if f[5] != "24K" or f[19] == "X" or f[16] not in cand:
            continue
        try:
            if float(f[14]) <= 0:
                continue
        except ValueError:
            continue
        nrec += 1
        batches[(f[0], _period(f[13], window_days))].add(f[16])
        donors[f[16]].add(f[0])
    keep_c = {c for c, d in donors.items() if len(d) >= min_donors}
    elig = {
        k: frozenset(v) for k, v in batches.items() if v <= keep_c and 1 <= len(v) <= HEAD_LIMIT
    }
    per = collections.Counter(k[0] for k in elig)
    keep_m = {m for m, n in per.items() if n >= min_batches}
    elig = {k: v for k, v in elig.items() if k[0] in keep_m}
    cands = sorted({h for v in elig.values() for h in v})
    comms = sorted(keep_m)
    ci = {c: i for i, c in enumerate(comms)}
    ki = {c: i for i, c in enumerate(cands)}
    cnt = collections.Counter()
    dates = collections.defaultdict(list)
    for (m, dte), H in elig.items():
        key = (ci[m], frozenset(ki[h] for h in H))
        cnt[key] += 1
        dates[key].append(dte)
    case = FECCase()
    case.name = f"fec{str(cycle)[2:]}" + (f"w{window_days}" if window_days else "")
    case.cycle = cycle
    case.comms, case.cands = comms, cands
    case.C, case.K = len(comms), len(cands)
    case.types = sorted(cnt, key=lambda t: (t[0], sorted(t[1])))
    case.counts = [cnt[t] for t in case.types]
    case.complete = set(case.types)
    case.accounting = {
        "records_24K_HS": nrec,
        "batches_all": len(batches),
        "batches_eligible": int(sum(case.counts)),
        "hyperarcs": len(case.types),
        "committees": case.C,
        "candidates": case.K,
        "batches_dropped_size": int(sum(1 for v in batches.values() if len(v) > HEAD_LIMIT)),
    }
    # candidate covariates
    party = np.array([cand[c]["party"] for c in cands])
    case.cand_rep = (party == "REP").astype(float)
    case.cand_dem = (party == "DEM").astype(float)
    case.cand_group = np.where(party == "REP", 1, np.where(party == "DEM", 0, 2))
    case.cand_state = np.array([cand[c]["state"] for c in cands])
    case.cand_senate = np.array([cand[c]["office"] == "S" for c in cands], float)
    case.cand_incumbent = np.array([cand[c]["ici"] == "I" for c in cands], float)
    d = pd.read_csv(
        dime_path,
        low_memory=False,
        usecols=["cycle", "recipient.type", "Cand.ID", "recipient.cfscore"],
    )
    d = d[(d.cycle == cycle) & (d["recipient.type"] == "cand")].dropna(subset=["recipient.cfscore"])
    cf = d.groupby("Cand.ID")["recipient.cfscore"].mean().to_dict()
    score = np.array([cf.get(c, np.nan) for c in cands])
    for g in (0, 1, 2):
        sel = (case.cand_group == g) & np.isnan(score)
        if sel.any():
            score[sel] = (
                np.nanmean(score[case.cand_group == g])
                if (case.cand_group == g).any() and not np.isnan(score[case.cand_group == g]).all()
                else np.nanmean(score)
            )
    case.cand_cf = score
    case.cand_cf_missing = int(sum(c not in cf for c in cands))
    case.comm_state = np.array([comm.get(m, {}).get("state", "") for m in comms])
    case.comm_type = np.array([comm.get(m, {}).get("type", "") for m in comms])
    case.comm_org = np.array([comm.get(m, {}).get("org", "") for m in comms])
    case.comm_dsgn = np.array([comm.get(m, {}).get("dsgn", "") for m in comms])
    case.same_state = (case.comm_state[:, None] == case.cand_state[None, :]).astype(float)
    case.neg_seed = 20261104 + cycle
    return case


def activity(case):
    a = np.zeros(case.C)
    for (s, H), c in zip(case.types, case.counts, strict=False):
        a[s] += c * len(H)
    return a


def mask(case, mech, rep, q=0.30):
    rng = np.random.default_rng(case.neg_seed + 1000 * rep + (0 if mech == "MCAR" else 500))
    m = len(case.types)
    if mech == "MCAR":
        out = np.zeros(m, bool)
        out[rng.choice(m, int(q * m), replace=False)] = True
        return out
    a = activity(case)
    x = np.array([a[s] for s, _ in case.types])
    lo, hi = 0.0, 1.0 / x.min()
    for _ in range(100):
        lam = (lo + hi) / 2
        if np.minimum(1, lam * x).mean() < q:
            lo = lam
        else:
            hi = lam
    return rng.random(m) < np.minimum(1, lam * x)


def training(case, m):
    Y = np.zeros((case.C, case.K), np.int8)
    W = np.zeros((case.C, case.K))
    bills = np.zeros(case.C)
    for (s, H), c, mm in zip(case.types, case.counts, m, strict=False):
        if not mm:
            Hl = list(H)
            Y[s, Hl] = 1
            W[s, Hl] += c
            bills[s] += c
    return Y, W, bills


def negatives(case, pos, Y, mech, rep, kind, lean=None):
    """Random, party-matched or head-perturbation alternatives (one per positive)."""
    rnd = random.Random(
        case.neg_seed
        + 7919 * rep
        + {"random": 0, "matched": 1, "perturb": 2}[kind]
        + (0 if mech == "MCAR" else 3001)
    )
    active_c = np.nonzero(Y.sum(1) > 0)[0].tolist()
    active_k = np.nonzero(Y.sum(0) > 0)[0].tolist()
    groups = collections.defaultdict(list)
    for k in active_k:
        groups[int(case.cand_group[k])].append(k)
    lean_cls = None
    if lean is not None:
        lean_cls = (lean > 0.5).astype(int)
        by_cls = collections.defaultdict(list)
        for c in active_c:
            by_cls[int(lean_cls[c])].append(c)
    used, out = set(), []
    for s, H in pos:
        acc = None
        comp = collections.Counter(int(case.cand_group[h]) for h in H)
        for _ in range(20000):
            if kind == "random":
                s2 = rnd.choice(active_c)
                H2 = frozenset(rnd.sample(active_k, len(H)))
            elif kind == "matched":
                s2 = rnd.choice(by_cls[int(lean_cls[s])])
                H2 = []
                ok = True
                for g, k in sorted(comp.items()):
                    if len(groups[g]) < k:
                        ok = False
                        break
                    H2 += rnd.sample(groups[g], k)
                if not ok:
                    break
                H2 = frozenset(H2)
            else:
                s2 = s
                h = rnd.choice(sorted(H))
                j = rnd.choice(active_k)
                if j in H:
                    continue
                H2 = frozenset((H - {h}) | {j})
            key = (s2, H2)
            if key in case.complete or key in used or key == (s, H):
                continue
            used.add(key)
            acc = key
            break
        out.append(acc)
    return out
