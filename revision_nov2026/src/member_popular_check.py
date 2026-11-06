import pickle, glob, sys, collections, numpy as np
sys.path.insert(0, '.')
from summary_member import rank_stats
"""MRR when the hidden supporter is one of the nine most active actors versus other tasks.

Usage: python member_popular_check.py RESULTS_DIR
"""
res = sys.argv[1]
for case in ["s118","s117","s116","h118","fec24","fec22"]:
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted(glob.glob(f"{res}/member_{case}/*.pkl")):
        r = pickle.load(open(f,"rb"))
        cnt = collections.Counter(x for t in r["tasks"] for x in t[3][1:10])
        T = {x for x,_ in cnt.most_common(9)}
        for t, row in zip(r["tasks"], r["scores"]):
            v = t[2]; g = "top" if v in T else "other"
            for k in ("NHPD_maxmin","NHPD_mean","HM","coparticipation","LR","BM"):
                if k in row[0]:
                    out[g][k].append(rank_stats([c[k] for c in row])[0])
    print(case, {g:(len(d["NHPD_maxmin"]), {k:round(np.mean(v),3) for k,v in d.items()}) for g,d in out.items()})
