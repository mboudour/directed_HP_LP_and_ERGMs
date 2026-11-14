"""Reduce a DIME contribDB file to one row per committee contributor.

Usage (on your own computer, Python 3 with pandas):
    python dime_committee_scores.py contribDB_2022.csv.gz committees_2022.csv.gz
    python dime_committee_scores.py contribDB_2024.csv.gz committees_2024.csv.gz

Reads the file in chunks (low memory), keeps only rows whose contributor is a
committee, and writes one row per committee (DIME id, name, state, FEC filer id,
CFscore, number of contributions, total amount). The output is a few MB.
"""

import sys

import pandas as pd

src, out = sys.argv[1], sys.argv[2]
use = [
    "cycle",
    "transaction.type",
    "amount",
    "bonica.cid",
    "contributor.name",
    "contributor.type",
    "contributor.state",
    "efec.comid.orig",
    "contributor.cfscore",
]
keys = ["bonica.cid", "contributor.name", "contributor.state", "efec.comid.orig"]

parts, n = [], 0
reader = pd.read_csv(
    src,
    usecols=use,
    chunksize=2_000_000,
    dtype=str,
    encoding="latin-1",
    on_bad_lines="skip",
    low_memory=False,
)
for chunk in reader:
    n += len(chunk)
    parts.append(chunk[chunk["contributor.type"].str.upper().eq("C")])
    print(f"read {n:,} rows, committee rows so far {sum(len(p) for p in parts):,}", flush=True)

d = pd.concat(parts, ignore_index=True)
d["contributor.cfscore"] = pd.to_numeric(d["contributor.cfscore"], errors="coerce")
d["amount"] = pd.to_numeric(d["amount"], errors="coerce")
d["is24K"] = d["transaction.type"].str.upper().eq("24K")
g = (
    d.groupby(keys, dropna=False)
    .agg(
        cfscore=("contributor.cfscore", "mean"),
        n_contributions=("amount", "size"),
        n_24K=("is24K", "sum"),
        total_amount=("amount", "sum"),
    )
    .reset_index()
)
g.to_csv(out, index=False, compression="gzip")
print(f"wrote {len(g):,} rows to {out}")
