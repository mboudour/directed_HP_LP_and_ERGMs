"""Ordered event types, projection, caps and formal-concept enumeration."""

import collections

import numpy as np


def valid_events(bills, universe):
    """Return list of (bill_id, sponsor, frozenset(head)) for nonempty-head bills
    with one sponsor, all participants inside the universe."""
    out, dropped = [], collections.Counter()
    for b in bills:
        if len(b["sponsors"]) != 1:
            dropped["sponsor_count"] += 1
            continue
        s = b["sponsors"][0]
        H = frozenset(b["original_cosponsors"]) - {s}
        if not H:
            dropped["empty_head"] += 1
            continue
        if s not in universe or not H <= set(universe):
            dropped["outside_universe"] += 1
            continue
        out.append((f"{b['type']}{b['number']}", s, H))
    return out, dropped


def group_types(events):
    """Group identical ordered (sponsor, head) pairs into types with counts."""
    cnt = collections.Counter((s, H) for _, s, H in events)
    members = collections.defaultdict(list)
    for bid, s, H in events:
        members[(s, H)].append(bid)
    return cnt, members


def projection(types, idx, n):
    Y = np.zeros((n, n), dtype=np.int8)
    for s, H in types:
        i = idx[s]
        for h in H:
            Y[i, idx[h]] = 1
    return Y


def concepts(Y, cT, cH):
    """All formal concepts (T,H) of binary relation Y with 1<=|T|<=cT, 1<=|H|<=cH.

    Enumerated from closures of tails: every concept tail is the closure of
    some set; we search tails by combining successor-set intersections.
    For cT small we enumerate closures H = T^up for all T with |T|<=cT and
    keep pairs whose closure T' = H^down has |T'|<=cT.
    """
    n = Y.shape[0]
    out_sets = [frozenset(np.nonzero(Y[i])[0]) for i in range(n)]
    in_sets = [frozenset(np.nonzero(Y[:, j])[0]) for j in range(n)]
    found = set()
    # level-wise: candidate tails of size 1..cT with nonempty common successors
    frontier = {frozenset([i]): out_sets[i] for i in range(n) if out_sets[i]}
    for size in range(1, cT + 1):
        nxt = {}
        for T, H in frontier.items():
            if not H:
                continue
            # closure
            Tc = frozenset.intersection(*[in_sets[j] for j in H])
            if 1 <= len(Tc) <= cT and 1 <= len(H) <= cH:
                found.add((Tc, H))
            if size < cT:
                for k in range(max(T) + 1, n):
                    H2 = H & out_sets[k]
                    if H2:
                        nxt[T | {k}] = H2
        frontier = nxt
    return found


def concepts_bitset(Y, cT, cH):
    """Memory-light equivalent of `concepts` using integer bitsets and depth-first search."""
    n = Y.shape[0]
    out_m = [sum(1 << int(j) for j in np.nonzero(Y[i])[0]) for i in range(n)]
    in_m = [sum(1 << int(i) for i in np.nonzero(Y[:, j])[0]) for j in range(n)]
    full = (1 << n) - 1

    def members(m):
        out, k = [], 0
        while m:
            if m & 1:
                out.append(k)
            m >>= 1
            k += 1
        return out

    found = set()

    def visit(last, H, depth):
        if H.bit_count() <= cH:
            Tc = full
            for j in members(H):
                Tc &= in_m[j]
            if Tc.bit_count() <= cT:
                found.add((frozenset(members(Tc)), frozenset(members(H))))
        if depth < cT:
            for k in range(last + 1, n):
                H2 = H & out_m[k]
                if H2:
                    visit(k, H2, depth + 1)

    for i in range(n):
        if out_m[i]:
            visit(i, out_m[i], 1)
    return found
