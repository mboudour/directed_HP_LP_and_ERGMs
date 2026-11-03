import os
from pathlib import Path

import casesetup
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

# Input folders (public data, never committed). Override with environment variables.
_ROOT = Path(__file__).resolve().parents[2]
RAW = os.environ.get("REVISION_RAW", str(_ROOT / "data" / "raw" / "revision_nov2026")) + "/"
PROC = os.environ.get("REVISION_PROC", str(_ROOT / "data" / "processed" / "revision_nov2026")) + "/"
LEG = [RAW + "legislators-current.yaml", RAW + "legislators-historical.yaml"]
CASES = {
    "s118": ("bills_118-s.json", "sen", 118, ["S118", "S117", "H118", "H117", "H116"]),
    "s117": ("bills_117-s.json", "sen", 117, ["S117", "S116", "H117", "H116", "H115"]),
    "s116": ("bills_116-s.json", "sen", 116, ["S116", "S115", "H116", "H115", "H114"]),
    "h118": ("bills_118-hr.json", "rep", 118, ["H118", "H117", "S118", "H116"]),
}


def make_case(name, **kw):
    f, ch, c, noms = CASES[name]
    return casesetup.Case(
        name, PROC + f, ch, c, LEG, [RAW + f"{m}_members.csv" for m in noms], **kw
    )


def pr(pairs, key, sel=None):
    pos = [a[key] for k, (a, b, *_) in enumerate(pairs) if sel is None or sel[k]]
    neg = [b[key] for k, (a, b, *_) in enumerate(pairs) if sel is None or sel[k]]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    sc = np.r_[pos, neg]
    return average_precision_score(y, sc), roc_auc_score(y, sc)
