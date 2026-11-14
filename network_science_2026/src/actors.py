"""Actor universe and fixed covariates for one chamber and Congress.

Universe: every person (Bioguide ID) with a term in the chamber that overlaps
the Congress dates (all-serving-persons rule; no merging by seat).
Covariates: party at the start of the person's service in the Congress,
state, first-dimension DW-NOMINATE (Voteview; fallback to the most recent
earlier Congress or other chamber), majority-caucus membership, and completed
years of prior service in the same chamber before entry into this Congress.
"""

import csv
import datetime as dt

import yaml

CONGRESS_DATES = {
    116: ("2019-01-03", "2021-01-03"),
    117: ("2021-01-03", "2023-01-03"),
    118: ("2023-01-03", "2025-01-03"),
}
# Majority caucus by (chamber, congress). Independents caucusing with the
# Democrats are assigned to the Democratic caucus.
MAJORITY = {("sen", 116): "R", ("sen", 117): "D", ("sen", 118): "D", ("rep", 118): "R"}


def _d(s):
    return dt.date.fromisoformat(s)


def load_legislators(paths):
    people = []
    for p in paths:
        with open(p) as f:
            people.extend(yaml.safe_load(f))
    return people


def caucus(party):
    if party in ("Democrat", "Independent"):
        return "D"
    if party == "Republican":
        return "R"
    return party


def party_at(term, date):
    """Party on a date, honouring within-term party_affiliations."""
    for pa in term.get("party_affiliations", []) or []:
        if _d(pa["start"]) <= date < _d(pa["end"]) or (
            _d(pa["start"]) <= date and date == _d(pa["end"])
        ):
            return pa["party"]
    return term.get("party")


def build_universe(people, chamber, congress):
    c0, c1 = map(_d, CONGRESS_DATES[congress])
    actors = {}
    for p in people:
        bid = p["id"].get("bioguide")
        terms = [t for t in p["terms"] if t["type"] == chamber]
        inside = [t for t in terms if _d(t["start"]) < c1 and _d(t["end"]) > c0]
        if not bid or not inside:
            continue
        first = min(inside, key=lambda t: t["start"])
        entry = max(_d(first["start"]), c0)
        party = party_at(first, entry)
        prior_days = 0
        for t in terms:
            s, e = _d(t["start"]), min(_d(t["end"]), entry)
            if s < entry and e > s:
                prior_days += (e - s).days
        actors[bid] = {
            "bioguide": bid,
            "name": p["name"].get("official_full")
            or f"{p['name'].get('first')} {p['name'].get('last')}",
            "party": party,
            "caucus": caucus(party),
            "state": first["state"],
            "entry": entry.isoformat(),
            "seniority": int(prior_days // 365.25),
            "majority": int(caucus(party) == MAJORITY[(chamber, congress)]),
            "reference_date_member": any(
                _d(t["start"]) <= c0 + dt.timedelta(days=0) < _d(t["end"])
                or _d(t["start"]) <= c0 < _d(t["end"])
                for t in inside
            ),
        }
    return actors


def load_nominate(paths_in_priority):
    """Map bioguide -> (dim1, source); earlier paths take priority."""
    out = {}
    for path in paths_in_priority:
        with open(path) as f:
            for r in csv.DictReader(f):
                b, v = r.get("bioguide_id"), r.get("nominate_dim1")
                if b and v not in (None, "") and b not in out:
                    out[b] = (float(v), path.rsplit("/", 1)[-1])
    return out
