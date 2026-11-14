"""Build one analysis case: actors, covariates, event types, masks, constraints.

Mask and random-negative draws follow the frozen-split contract of the
published pipeline (scripts/36 and scripts/37 of the repository): event types
are sorted by (tail, head) Bioguide tuples, masks use Python's Random with the
recorded split seeds, and random negatives are drawn with Random.sample over
the sorted node tuple, subject to type exclusion, uniqueness, weak-distance-two
locality and all-date service feasibility.
"""

import collections
import datetime as dt
import json
import math
import random

import actors
import events
import numpy as np

MECH_OFFSET_MASK = {"MCAR": 0, "MNAR-out": 52_361}
MECH_OFFSET_NEG = {"MCAR": 0, "MNAR-out": 5_003}


class Case:
    def __init__(
        self,
        name,
        bills_path,
        chamber,
        congress,
        legislators,
        nominate_paths,
        head_cap=10,
        tail_cap=1,
        base_seed=20261026,
        neg_seed=20261013,
    ):
        self.name, self.chamber, self.congress = name, chamber, congress
        self.base_seed, self.neg_seed = base_seed, neg_seed
        people = actors.load_legislators(legislators)
        U = actors.build_universe(people, chamber, congress)
        self.U = U
        self.nodes = tuple(sorted(U))
        self.idx = {b: i for i, b in enumerate(self.nodes)}
        n = self.n = len(self.nodes)
        bills = json.load(open(bills_path))
        self.bills = bills
        ev, self.dropped = events.valid_events(bills, U)
        self.events = ev
        cnt, members = events.group_types(ev)
        self.all_types_count = cnt
        intro = {f"{b['type']}{b['number']}": b["introduced"] for b in bills}
        T = sorted(((s,), tuple(sorted(H))) for (s, H) in cnt if len(H) <= head_cap)
        self.types_str = T
        self.counts = [cnt[(t[0][0], frozenset(t[1]))] for t in T]
        self.types = [(self.idx[t[0][0]], frozenset(self.idx[h] for h in t[1])) for t in T]
        self.type_dates = {}
        for t, ti in zip(T, self.types, strict=False):
            ds = sorted({intro[b] for b in members[(t[0][0], frozenset(t[1]))]})
            self.type_dates[ti] = [dt.date.fromisoformat(d) for d in ds]
        self.complete = set(self.types)
        self.noncap = [
            (self.idx[s], frozenset(self.idx[h] for h in H)) for (s, H) in cnt if len(H) > head_cap
        ]
        self.train_uncapped = False
        # projections
        self.Ycap = events.projection([(s, H) for s, H in self.types], {i: i for i in range(n)}, n)
        self.Yall = events.projection(list(cnt), self.idx, n)
        # service intervals in the chamber
        self.terms = collections.defaultdict(list)
        for p in people:
            b = p["id"].get("bioguide")
            if b in self.idx:
                for t in p["terms"]:
                    if t["type"] == chamber:
                        self.terms[self.idx[b]].append(
                            (dt.date.fromisoformat(t["start"]), dt.date.fromisoformat(t["end"]))
                        )
        # covariates
        nom = actors.load_nominate(nominate_paths)
        self.nominate_source = {}
        z = np.zeros(n)
        for b, i in self.idx.items():
            if b in nom:
                z[i] = nom[b][0]
                self.nominate_source[b] = nom[b][1]
            else:
                z[i] = np.nan
        if np.isnan(z).any():
            z[np.isnan(z)] = np.nanmean(z)
        party_codes = {p: k for k, p in enumerate(sorted({a["party"] for a in U.values()}))}
        caucus_codes = {"D": 0, "R": 1}
        state_codes = {s: k for k, s in enumerate(sorted({a["state"] for a in U.values()}))}
        self.cov = {
            "party": np.array([party_codes[U[b]["party"]] for b in self.nodes]),
            "caucus": np.array([caucus_codes.get(U[b]["caucus"], 2) for b in self.nodes]),
            "state": np.array([state_codes[U[b]["state"]] for b in self.nodes]),
            "nominate": z,
            "majority": np.array([U[b]["majority"] for b in self.nodes], float),
            "seniority": np.array([U[b]["seniority"] for b in self.nodes], float),
        }
        self._mnar_p = None

    # ------------------------------------------------------------ masks
    def mask(self, mech, replicate, q=0.30):
        N = len(self.types)
        seed = self.base_seed + 104_729 * replicate + MECH_OFFSET_MASK[mech]
        rnd = random.Random(seed)
        if mech == "MCAR":
            sel = set(rnd.sample(range(N), min(math.floor(q * N), N - 1)))
        else:
            if self._mnar_p is None:
                inc = collections.Counter()
                for (s, H), c in zip(self.types, self.counts, strict=False):
                    inc[s] += c * len(H)
                w = [inc[s] for s, H in self.types]
                target = q * N
                lo, hi = 0.0, 1.0 / min(w)
                while sum(min(1.0, hi * x) for x in w) < target:
                    hi *= 2
                for _ in range(80):
                    m = (lo + hi) / 2
                    if sum(min(1.0, m * x) for x in w) < target:
                        lo = m
                    else:
                        hi = m
                self._mnar_p = [min(1.0, hi * x) for x in w]
            sel = {i for i, p in enumerate(self._mnar_p) if rnd.random() < p}
        m = np.zeros(N, bool)
        m[list(sel)] = True
        return m, seed

    def serves(self, i, d):
        return any(s <= d < e for s, e in self.terms.get(i, ()))

    def serve_ok(self, participants, dates):
        return all(self.serves(int(p), d) for p in participants for d in dates)

    # ------------------------------------------------------------ negatives
    def random_negatives(self, positives, R, mech, replicate):
        """Exact replica of the published temporal random-negative sampler."""
        rnd = random.Random(self.neg_seed + 10_007 * replicate + MECH_OFFSET_NEG[mech])
        nodes = list(range(self.n))  # sorted Bioguide order == index order
        used, out, audit = set(), [], collections.Counter()
        for s, H in positives:
            k = len(H)
            dates = self.type_dates[(s, H)]
            acc = None
            for _ in range(100_000):
                audit["attempts"] += 1
                pick = rnd.sample(nodes, 1 + k)
                key = (pick[0], frozenset(pick[1:]))
                if key in self.complete:
                    continue
                if key in used:
                    continue
                if not R[np.ix_(pick, pick)].all():
                    continue
                if not self.serve_ok(pick, dates):
                    audit["service_rejections"] += 1
                    continue
                used.add(key)
                acc = key
                break
            out.append(acc)
        return out, audit
