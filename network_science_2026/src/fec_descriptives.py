import sys, numpy as np, collections
sys.path.insert(0,'.')
import fec_case as F
for y,c in (("24",2024),("22",2022)):
    case=F.build_case(f"../../fec{y}","../../dime/recipients.csv.gz",c)
    Y=np.zeros((case.C,case.K),bool)
    for s,H in case.types: Y[s,list(H)]=True
    dates=[len(case.type_dates[t]) for t in case.types]
    attrs=[a for a in dir(case) if not a.startswith('_')]
    print(c,'C',case.C,'K',case.K,'types',len(case.types),'density',round(Y.mean(),4),'recur>1date',round(np.mean(np.array(dates)>1),4),'mean recipients',round(Y.sum(1).mean(),2))
    print(' senate',int(np.sum(case.cand_senate)),'incumbent share',round(float(np.mean(case.cand_incumbent)),3))
