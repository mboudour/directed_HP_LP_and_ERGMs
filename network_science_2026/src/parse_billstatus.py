"""Parse GPO Bill Status XML archives into introduction-time ordered events.

One record = one bill. Tail = the single recorded sponsor (Bioguide ID).
Head = distinct co-sponsors with isOriginalCosponsor == True (withdrawn
original co-sponsors are retained: the target is membership at introduction).

Usage: python -I parse_billstatus.py ZIP OUT.json
"""

import json
import sys
import zipfile

from lxml import etree


def _text(node, path):
    x = node.find(path)
    return x.text.strip() if x is not None and x.text else None


def parse_record(xml_bytes):
    root = etree.fromstring(xml_bytes)
    bill = root.find("bill")
    rec = {
        "congress": _text(bill, "congress"),
        "type": _text(bill, "type"),
        "number": _text(bill, "number"),
        "introduced": _text(bill, "introducedDate"),
        "policy_area": _text(bill, "policyArea/name"),
        "committees": sorted(
            {c.text for c in bill.findall("committees/item/systemCode") if c.text}
        ),
    }
    sponsors = [s for s in (_text(i, "bioguideId") for i in bill.findall("sponsors/item")) if s]
    rec["sponsors"] = sponsors
    orig, withdrawn, later, dup = [], [], [], 0
    seen = set()
    for c in bill.findall("cosponsors/item"):
        bid = _text(c, "bioguideId")
        if not bid:
            continue
        is_orig = (_text(c, "isOriginalCosponsor") or "").lower() == "true"
        if is_orig:
            if bid in seen:
                dup += 1
                continue
            seen.add(bid)
            orig.append(bid)
            if _text(c, "sponsorshipWithdrawnDate"):
                withdrawn.append(bid)
        else:
            later.append(bid)
    rec["original_cosponsors"] = orig
    rec["withdrawn_original"] = withdrawn
    rec["later_cosponsors"] = later
    rec["duplicate_original_rows"] = dup
    return rec


def main(zpath, out):
    recs = []
    with zipfile.ZipFile(zpath) as z:
        for name in sorted(z.namelist()):
            if name.endswith(".xml"):
                recs.append(parse_record(z.read(name)))
    with open(out, "w") as f:
        json.dump(recs, f)
    n = len(recs)
    one = sum(len(r["sponsors"]) == 1 for r in recs)
    ne = sum(len(r["sponsors"]) == 1 and len(r["original_cosponsors"]) > 0 for r in recs)
    print(
        f"{zpath}: records={n} single_sponsor={one} nonempty_head={ne} "
        f"withdrawn_orig={sum(len(r['withdrawn_original']) for r in recs)} "
        f"dup_rows={sum(r['duplicate_original_rows'] for r in recs)}"
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
