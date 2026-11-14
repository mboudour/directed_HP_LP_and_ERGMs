# ruff: noqa: E501
"""Match FEC committees to DIME contributor CFscores by normalized name (and state).

DIME contribDB rows of committee contributors (contributor.type C), reduced to one row per
(bonica.cid, contributor.name, contributor.state, efec.comid.orig) by dime_committee_scores.py.
efec.comid.orig is the filing (recipient) committee, so matching uses names.
"""

import re

import numpy as np
import pandas as pd

STOP = {
    "the",
    "inc",
    "incorporated",
    "pac",
    "political",
    "action",
    "committee",
    "cmte",
    "comm",
    "fund",
    "federal",
    "of",
    "and",
    "for",
    "a",
    "an",
    "aka",
    "also",
    "known",
    "as",
    "llc",
    "corp",
    "corporation",
    "co",
    "company",
    "employees",
    "employee",
    "good",
    "government",
}


def norm(s, drop_stop=False):
    s = re.sub(r"\(.*?\)", " ", str(s).lower())
    s = s.replace("&", " and ")
    toks = re.sub(r"[^a-z0-9 ]", " ", s).split()
    if drop_stop:
        toks = [t for t in toks if t not in STOP]
    return " ".join(toks)


def committee_scores(cm_path, dime_cm_path, comms):
    names = {}
    for line in open(cm_path, encoding="latin-1"):
        f = line.rstrip("\n").split("|")
        names[f[0]] = (f[1], f[6], f[13] if len(f) > 13 else "")
    d = pd.read_csv(dime_cm_path, dtype=str)
    d["cfscore"] = pd.to_numeric(d["cfscore"], errors="coerce")
    d["w"] = pd.to_numeric(d["n_contributions"], errors="coerce").fillna(1)
    d = d.dropna(subset=["cfscore"])
    out, how = np.full(len(comms), np.nan), np.array([""] * len(comms), dtype=object)
    for drop in (False, True):
        d["k"] = d["contributor.name"].map(lambda s, drop=drop: norm(s, drop))
        d["ks"] = d["k"] + "|" + d["contributor.state"].fillna("")
        for key, lab in (("ks", "name+state"), ("k", "name")):
            sub = d[d[key].str.len() > 3]
            # one score per key: weighted mean of distinct contributors; flag ambiguous keys
            g = sub.groupby(key).apply(
                lambda x: pd.Series(
                    {
                        "cf": np.average(x.cfscore, weights=x.w),
                        "sd": x.cfscore.std(ddof=0),
                        "ncid": x["bonica.cid"].nunique(),
                    }
                )
            )
            g = g[(g.ncid == 1) | (g.sd < 0.1)]
            for i, m in enumerate(comms):
                if not np.isnan(out[i]) or m not in names:
                    continue
                nm, st, _ = names[m]
                k = norm(nm, drop) + ("|" + st if key == "ks" else "")
                if k in g.index:
                    out[i] = g.at[k, "cf"]
                    how[i] = lab + (" (reduced)" if drop else "")
    return out, how
