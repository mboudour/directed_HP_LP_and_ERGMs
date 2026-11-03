# ruff: noqa: E501
"""Tables of the third benchmark run (estimated decay, structural zeros, head perturbation).

Usage: python make_tables_v3.py SUMMARY_V3_JSON COEF_V3_JSON CLOSURE_JSON TABLES_DIR
"""

import json
import sys

S = json.load(open(sys.argv[1]))
C = json.load(open(sys.argv[2]))
K = json.load(open(sys.argv[3]))
T = sys.argv[4]
MECHS = [("MCAR", "MCAR"), ("MNAR-out", "MNAR-out")]
CASES = [
    ("s118", "118th Senate"),
    ("s117", "117th Senate"),
    ("s116", "116th Senate"),
    ("h118", "118th House"),
]
NAMES = {
    "aa_total": "directed Adamic--Adar",
    "aa_oi": "Adamic--Adar, two-paths",
    "degprod": "degree product",
    "sponsor_activity": "initiator out-degree",
    "sponsor_bills": "initiator bill count",
    "bills_null": "bill-count draw",
    "observed_fraction": "observed footprint share",
    "weighted_footprint": "weighted footprint",
    "party_share": "same-party share",
    "M5_t05": "M5, $\\tau=0.5$",
    "M4c": "M4c",
    "M5": "M5",
    "M6": "M6",
    "S0": "S0",
    "S1": "S1",
    "SI": "SI",
    "chance": "chance",
}


def f3(x):
    return f"{x:.3f}".replace("-0.000", "0.000")


def table(path, caption, label, cols, header, rows, note, resize=False):
    lines = [
        r"\begin{table}[tbp]",
        r"\centering",
        r"\small",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
    ]
    if resize:
        lines.append(r"\resizebox{\textwidth}{!}{%")
    lines += [rf"\begin{{tabular}}{{{cols}}}", r"\toprule"] + header + [r"\midrule"]
    lines += [r + r" \\" for r in rows]
    lines += [r"\bottomrule", r"\end{tabular}"]
    if resize:
        lines.append("}")
    lines += [rf"\par\vspace{{2pt}}\footnotesize {note}", r"\end{table}", ""]
    open(f"{T}/{path}", "w").write("\n".join(lines))


SETS = [("random", "R"), ("matched", "P"), ("perturb", "H"), ("sub", "S")]

# ------------------------------------------------------------ performance, 118th Senate
rows = []
for k in [
    "aa_total",
    "aa_oi",
    "degprod",
    "sponsor_activity",
    "sponsor_bills",
    "observed_fraction",
    "weighted_footprint",
    "party_share",
    "M5_t05",
    "M4c",
    "M5",
    "M6",
    "S0",
    "S1",
    "SI",
]:
    cells = []
    for mech, _ in MECHS:
        M = S["s118"][mech]
        cells += [f3(M[s][k]["concordance"][0]) for s, _ in SETS]
        cells.append(f3(M["role"][k]["top1"][0]))
    rows.append(NAMES[k] + " & " + " & ".join(cells))
for k in ["chance", "bills_null"]:
    cells = []
    for mech, _ in MECHS:
        cells += ["0.500" if k == "chance" else "--"] * 4 + [
            f3(S["s118"][mech]["role"][k]["top1"][0])
        ]
    rows.append(NAMES[k] + " & " + " & ".join(cells))
table(
    "v3_performance.tex",
    "118th Senate: mean within-pair concordance on the random (R), party-matched (P), head-perturbation (H) and substitution (S) candidate sets, and top-1 accuracy on the role-assignment sets (A), over 30 masks per mechanism.",
    "tab:senate-performance",
    "l" + "r" * 10,
    [
        r" & \multicolumn{5}{c}{MCAR} & \multicolumn{5}{c}{MNAR-out} \\",
        r"Score & R & P & H & S & A & R & P & H & S & A \\",
    ],
    rows,
    "Concordance is the share of pairs in which the recorded hyperarc scores above its alternative (ties count one half). "
    "Model scores are $L_{1g}$ from fits to the training 2-section: M4c--M6 by MPLE with decay selected by profile pseudolikelihood (M5, $\\tau=0.5$: fixed decay); "
    "S0, S1 and SI by exact MLE. The bill-count draw selects the initiator with probability proportional to the observed bill counts. Pooled PR-AUC values are in Supplementary Table~S4.",
    resize=True,
)


# ------------------------------------------------------------ contrasts, 118th Senate
def cell(c, tl):
    return f"{f3(c[0])} & [{f3(tl[0])}, {f3(tl[1])}]"


rows = []
for mech, lab in MECHS:
    M = S["s118"][mech]
    for s, slab in [("random", "R"), ("matched", "P"), ("perturb", "H")]:
        for x, y in [
            ("M5", "aa_total"),
            ("S1", "aa_total"),
            ("S1", "M5"),
            ("S1", "weighted_footprint"),
            ("M5", "M5_t05"),
        ]:
            v = M[s + "_contrasts"][f"{x} - {y}"]
            rows.append(
                f"{lab} & {slab} & {NAMES[x]} $-$ {NAMES[y]} & "
                + cell(v["concordance"], v["concordance_cluster"])
            )
    for x, y in [("S1", "M5"), ("S1", "degprod")]:
        v = M["sub_contrasts"][f"{x} - {y}"]
        rows.append(
            f"{lab} & S & {NAMES[x]} $-$ {NAMES[y]} & "
            + cell(v["concordance"], v["concordance_cluster"])
        )
    for x, y in [
        ("S1", "chance"),
        ("M5", "chance"),
        ("S1", "M5"),
        ("S1", "bills_null"),
        ("S1", "sponsor_bills"),
        ("S1", "SI"),
        ("M6", "M5"),
    ]:
        v = M["role_contrasts"][f"{x} - {y}"]
        rows.append(
            f"{lab} & A & {NAMES[x]} $-$ {NAMES[y]} & " + cell(v["top1"], v["top1_cluster"])
        )
table(
    "v3_contrasts.tex",
    "118th Senate: paired contrasts of concordance (R, P, H, S) and of top-1 accuracy (A).",
    "tab:senate-contrasts",
    "lllrl",
    [r"Mask & set & contrast & difference & 95\% interval \\"],
    rows,
    "Differences are means over 30 masks. Intervals are sponsor-bootstrap intervals: each replicate resamples the sponsors of the record, with all their withheld hyperarcs, and applies the resample to all masks.",
)

# ------------------------------------------------------------ bipartisan (party-matched sets)
rows = []
for c, clab in CASES:
    for mech, lab in MECHS:
        M = S[c][mech]
        cl = M["matched_classes"]
        b, sgl = cl["bipartisan"], cl["single_party"]
        rows.append(
            f"{clab} & {lab} & {f3(b['share'])} & "
            f"{f3(b['contrasts']['M5 - M4c'][0])} & {f3(sgl['contrasts']['M5 - M4c'][0])} & "
            f"{f3(b['contrasts']['S1 - S0'][0])} & {f3(sgl['contrasts']['S1 - S0'][0])}"
        )
table(
    "v3_bipartisan.tex",
    "Effect of the political covariates on concordance in the party-matched candidate sets, by coalition type.",
    "tab:bipartisan",
    "llrrrrr",
    [
        r" & & & \multicolumn{2}{c}{M5 $-$ M4c} & \multicolumn{2}{c}{S1 $-$ S0} \\",
        r"Case & mask & bipartisan share & bipartisan & single-party & bipartisan & single-party \\",
    ],
    rows,
    "A hyperarc is bipartisan if at least one original co-sponsor belongs to another caucus than the sponsor; Independents belong to the Democratic caucus. "
    "Party-matched alternatives have an initiator of the sponsor's caucus and the same number of co-sponsors from each caucus. Random-set results, size classes and intervals are in Supplementary Table~S9.",
    resize=True,
)

# ------------------------------------------------------------ coefficients
rows = []
for c, lab in CASES:
    r = C[c]
    m5, s1, si = r["M5_mple"], r["S1_mle"], r["SI_mle"]
    reg = r["S1_sender_regression"]
    rows.append(
        f"{lab} & {r['tau_hat']:.0f} & {f3(m5['mutual'])} & {f3(m5['gwodegree'])} & {f3(m5['gwidegree'])} & {f3(m5['nodematch_party'])} & {f3(m5['absdiff_nominate'])} & "
        f"{f3(s1['mutual'])} ({f3(r['S1_mle_info']['se']['mutual'])}) & {f3(s1['nodematch_party'])} ({f3(r['S1_mle_info']['se']['nodematch_party'])}) & {f3(s1['absdiff_nominate'])} ({f3(r['S1_mle_info']['se']['absdiff_nominate'])}) & "
        f"{f3(si['nodeocov_majority'])} & {f3(si['nodeocov_seniority'])} & {f3(r['S1_mle_actor_sd']['sender'])} & {f3(reg['r2_majority_seniority'])}"
    )
table(
    "v3_coefficients.tex",
    "Selected coefficients on the complete 2-section of eligible hyperarcs: M5 (MPLE, decay $\\hat\\tau$), S1 and SI (exact MLE).",
    "tab:coefficients",
    "l" + "r" * 13,
    [
        r" & & \multicolumn{5}{c}{M5} & \multicolumn{3}{c}{S1} & \multicolumn{2}{c}{SI} & \multicolumn{2}{c}{S1 sender effects} \\",
        r"Case & $\hat\tau$ & mutual & $G^+$ & $G^-$ & party & ideology & mutual & party & ideology & majority & seniority & SD & $R^2$ \\",
    ],
    rows,
    "Party: party matching; ideology: absolute difference in first-dimension DW-NOMINATE. Party matching and ideological distance are strongly collinear and are read jointly. "
    "SI replaces the sender effects of S1 by the initiator's majority-caucus membership and seniority (in years). SD: standard deviation of the S1 sender effects of actors with at least one arc. "
    "$R^2$: share of their variance explained by majority-caucus membership and seniority. Parentheses: standard errors of S1 from the inverse observed information; MPLE standard errors of M5 are not reported because they are unreliable for dependence models. Coefficients describe the fitted models and are not interpreted causally.",
    resize=True,
)

# ------------------------------------------------------------ four cases
items = [
    ("M5 $-$ directed AA, R", lambda M: M["random_contrasts"]["M5 - aa_total"]["concordance"]),
    ("S1 $-$ directed AA, R", lambda M: M["random_contrasts"]["S1 - aa_total"]["concordance"]),
    ("S1 $-$ M5, P", lambda M: M["matched_contrasts"]["S1 - M5"]["concordance"]),
    ("M5 $-$ directed AA, H", lambda M: M["perturb_contrasts"]["M5 - aa_total"]["concordance"]),
    (
        "S1 $-$ weighted footprint, H",
        lambda M: M["perturb_contrasts"]["S1 - weighted_footprint"]["concordance"],
    ),
    ("M5 $-$ M5 ($\\tau=0.5$), H", lambda M: M["perturb_contrasts"]["M5 - M5_t05"]["concordance"]),
    ("S1 $-$ degree product, S", lambda M: M["sub_contrasts"]["S1 - degprod"]["concordance"]),
    ("S1 top-1 $-$ chance, A", lambda M: M["role_contrasts"]["S1 - chance"]["top1"]),
    ("M5 top-1 $-$ chance, A", lambda M: M["role_contrasts"]["M5 - chance"]["top1"]),
    ("S1 $-$ M5, A", lambda M: M["role_contrasts"]["S1 - M5"]["top1"]),
    ("S1 $-$ bill-count draw, A", lambda M: M["role_contrasts"]["S1 - bills_null"]["top1"]),
    (
        "S1 $-$ initiator out-degree, A",
        lambda M: M["role_contrasts"]["S1 - sponsor_activity"]["top1"],
    ),
    ("S1 $-$ SI, A", lambda M: M["role_contrasts"]["S1 - SI"]["top1"]),
]
rows = []
for lab, fn in items:
    rows.append(lab + " & " + " & ".join(f3(fn(S[c][m])[0]) for c, _ in CASES for m, _ in MECHS))
table(
    "v3_cases.tex",
    "Main contrasts in all four cases: mean differences over 30 masks in concordance (R, P, H, S) or top-1 accuracy (A).",
    "tab:case-results",
    "l" + "r" * 8,
    [
        r" & \multicolumn{2}{c}{118th Senate} & \multicolumn{2}{c}{117th Senate} & \multicolumn{2}{c}{116th Senate} & \multicolumn{2}{c}{118th House} \\",
        r"Contrast & MCAR & MNAR-out & MCAR & MNAR-out & MCAR & MNAR-out & MCAR & MNAR-out \\",
    ],
    rows,
    "R, P, H, S, A: random, party-matched, head-perturbation, substitution and role-assignment candidate sets. Supplementary Table~S3 gives intervals.",
    resize=True,
)

# ------------------------------------------------------------ closure (unchanged design)
rows = []
for c, lab in CASES:
    k = K[c]
    rows.append(
        f"{lab} & {k['hyperarcs']:,} & {f3(k['share_equal_head_concept'])} & {k['mean_tail_size_head_concept']:.1f} & "
        f"{f3(k['mean_head_ratio'])} & {f3(k['mean_footprint_jaccard'])} & {f3(k['mean_head_over_outneighbourhood'])}"
    )
table(
    "v3_closure.tex",
    "Recorded hyperarcs and the formal concepts generated by their heads in the 2-section of all recorded hyperarcs, without size limits.",
    "tab:closure",
    "lrrrrrr",
    [
        r"Case & hyperarcs & equal to concept & $|H^{\downarrow}|$ & $|H|/|H^{\downarrow\uparrow}|$ & Jaccard & $|H|/|N^+(s)|$ \\"
    ],
    rows,
    "For a hyperarc $(\\{s\\},H)$ the generated concept is $(H^{\\downarrow},H^{\\downarrow\\uparrow})$, the concept with the smallest head containing $H$. "
    "Columns give the share of hyperarcs equal to their generated concept and means over hyperarcs of the size of its tail (which includes $s$), of the head ratio, "
    "of the Jaccard similarity of the two footprints, and of the head size relative to the sponsor's out-neighbourhood.",
    resize=True,
)

# ------------------------------------------------------------ SI: case intervals
rows = []
for c, lab in CASES:
    for m, ml in MECHS:
        M = S[c][m]
        for name, (setk, key, tk) in [
            ("M5 $-$ directed AA, R", ("random_contrasts", "M5 - aa_total", "concordance")),
            ("S1 $-$ M5, P", ("matched_contrasts", "S1 - M5", "concordance")),
            ("M5 $-$ directed AA, H", ("perturb_contrasts", "M5 - aa_total", "concordance")),
            ("S1 $-$ degree product, S", ("sub_contrasts", "S1 - degprod", "concordance")),
            ("S1 $-$ chance, A", ("role_contrasts", "S1 - chance", "top1")),
            ("M5 $-$ chance, A", ("role_contrasts", "M5 - chance", "top1")),
            ("S1 $-$ M5, A", ("role_contrasts", "S1 - M5", "top1")),
            ("S1 $-$ initiator out-degree, A", ("role_contrasts", "S1 - sponsor_activity", "top1")),
        ]:
            v = M[setk][key]
            cl = v[tk + "_cluster"]
            mc = v[tk]
            rows.append(
                f"{lab} & {ml} & {name} & {f3(mc[0])} & [{f3(mc[1])}, {f3(mc[2])}] & [{f3(cl[0])}, {f3(cl[1])}]"
            )
table(
    "v3_cases_ci.tex",
    "Main contrasts in all four cases with mask-bootstrap and sponsor-bootstrap intervals.",
    "tab:case-ci",
    "llllll",
    [r"Case & mask & contrast & difference & masks & sponsors \\"],
    rows,
    "R, P, H, S, A: random, party-matched, head-perturbation, substitution and role-assignment candidate sets; concordance for R, P, H, S and top-1 accuracy for A.",
    resize=True,
)

# ------------------------------------------------------------ SI: classes (118th Senate)
rows = []
for m, ml in MECHS:
    M = S["s118"][m]
    for s_, sl in [("random", "random"), ("matched", "party-matched")]:
        for cl, cll in [
            ("bipartisan", "bipartisan"),
            ("single_party", "single-party"),
            ("bipartisan_size_1_3", "bipartisan, 1--3"),
            ("single_party_size_1_3", "single-party, 1--3"),
            ("bipartisan_size_4_10", "bipartisan, 4--10"),
            ("single_party_size_4_10", "single-party, 4--10"),
            ("bipartisan_20", "at least 20\\% other caucus"),
        ]:
            v = M[s_ + "_classes"][cl]
            a = v["contrasts"]["M5 - M4c"]
            b = v["contrasts"]["S1 - S0"]
            rows.append(
                f"{ml} & {sl} & {cll} & {f3(v['share'])} & {f3(a[0])} [{f3(a[1])}, {f3(a[2])}] & {f3(b[0])} [{f3(b[1])}, {f3(b[2])}]"
            )
table(
    "v3_size_classes.tex",
    "118th Senate: effect of the political covariates on concordance by coalition type and number of original co-sponsors.",
    "tab:size-classes",
    "llllll",
    [r"Mask & candidate set & class & share & M5 $-$ M4c & S1 $-$ S0 \\"],
    rows,
    "The last class uses a share-based definition: at least 20\\% of the original co-sponsors belong to another caucus than the sponsor. Brackets: 95\\% mask-bootstrap intervals.",
    resize=True,
)

# ------------------------------------------------------------ SI: survival strata
rows = []
for m, ml in MECHS:
    M = S["s118"][m]
    for s_, sl in [("random", "R"), ("matched", "P"), ("perturb", "H")]:
        for cl, cll in [
            ("pos_surv", "recorded survives"),
            ("pos_not_surv", "recorded does not survive"),
            ("neither_surv", "neither survives"),
        ]:
            v = M[s_ + "_classes"][cl]
            cc = v["concordance"]
            rows.append(
                f"{ml} & {sl} & {cll} & {f3(v['share'])} & {f3(cc['M5'])} & {f3(cc['S1'])} & {f3(cc['aa_total'])} & {f3(cc['weighted_footprint'])} & {f3(cc['observed_fraction'])}"
            )
table(
    "v3_survival.tex",
    "118th Senate: concordance by survival of the footprints in the training 2-section.",
    "tab:survival",
    "lllrrrrrr",
    [
        r"Mask & set & stratum & share & M5 & S1 & directed AA & weighted footprint & observed share \\"
    ],
    rows,
    "A footprint survives if all its arcs are present in the training 2-section through other observed hyperarcs. The last stratum requires that neither the recorded hyperarc nor its alternative survives.",
    resize=True,
)

# ------------------------------------------------------------ SI: MLE check
rows = []
for c, lab in CASES:
    r = C[c]
    for mname in ["S0", "S1", "SI"]:
        inf = r[mname + "_mle_info"]
        diff = ""
        if mname + "_mple" in r:
            a, b = r[mname + "_mle"], r[mname + "_mple"]
            diff = f3(max(abs(a[t] - b[t]) for t in a if t in b))
        rows.append(
            f"{lab} & {mname} & {inf['dyads']:,} & {inf['observed_arcs']:,} & {inf['expected_arcs']:.3f} & {inf['observed_mutual']:,} & {inf['expected_mutual']:.3f} & {diff}"
        )
table(
    "v3_mle.tex",
    "Exact (ridge-penalized) MLE for S0, S1 and SI on the complete 2-sections: score equations and agreement with MPLE.",
    "tab:mle-mple",
    "llrrrrrr",
    [
        r"Case & model & dyads & arcs & expected & mutual & expected & max.\ $|\hat\theta_{\mathrm{MLE}}-\hat\theta_{\mathrm{MPLE}}|$ \\"
    ],
    rows,
    "Dyads excludes pairs of legislators whose service did not overlap. Expected counts are computed under the fitted model. The last column compares the coefficients of the arc, mutuality and covariate terms with the MPLE (computed without structural zeros).",
    resize=True,
)
print("v3 tables written")

# ------------------------------------------------------------ SI: simulations from the fitted models (optional)
if len(sys.argv) > 5:
    import csv

    R = sys.argv[5]
    src = [
        (
            f"{R}/mple_sim_s118/simulation_summary.csv",
            {"M4c": "M4c, $\\tau=0.5$", "M5": "M5, $\\tau=0.5$"},
        ),
        (
            f"{R}/mple_simulation_tau4/simulation_summary.csv",
            {"M4c": "M4c, $\\tau=4$", "M5": "M5, $\\tau=4$"},
        ),
        (f"{R}/gof_sr_s118/simulation_summary.csv", {"S0": "S0", "S1": "S1"}),
    ]
    STATS = {
        "edges": "arcs",
        "mutual": "mutual dyads",
        "ttriple": "transitive triples",
        "ctriple": "cyclic triples",
    }
    rows = []
    for path, models in src:
        for r in csv.DictReader(open(path)):
            if r["model"] in models and r["statistic"] in STATS:
                rows.append(
                    f"{models[r['model']]} & {STATS[r['statistic']]} & {float(r['observed']):,.0f} & {float(r['sim_mean']):,.0f} & "
                    f"[{float(r['sim_q025']):,.0f}, {float(r['sim_q975']):,.0f}]"
                )
    table(
        "v3_simulation.tex",
        "118th Senate: networks simulated from the fitted models on the complete 2-section compared with the observed network.",
        "tab:mle",
        "llrrl",
        [r"Model & statistic & observed & simulated mean & 95\% range \\"],
        rows,
        "One hundred networks per model, simulated with the statnet \\texttt{ergm} package (burn-in 200,000, interval 10,000) from the MPLE coefficients; "
        "for S1 the MPLE differs from the MLE (which has structural zeros) by up to 0.30 in the state-matching coefficient and by at most 0.04 in the other non-actor coefficients.",
    )
    print("simulation table written")


# ------------------------------------------------------------ SI: extra tables (optional inputs)
if len(sys.argv) > 8:
    E = json.load(open(sys.argv[6]))  # summary_v3_sens.json
    D = json.load(open(sys.argv[7]))  # decomp_v3_s118.json
    J = [json.load(open(x)) for x in sys.argv[8].split(",")]  # joint json per mechanism
    # role-assignment by class
    rows = []
    for c, lab in [("s118", "118th Senate"), ("h118", "118th House")]:
        for m, ml in MECHS:
            for cl, cll in [
                ("pair", "one co-sponsor"),
                ("size_2_3", "2--3 co-sponsors"),
                ("size_4_10", "4--10 co-sponsors"),
                ("bipartisan", "bipartisan"),
                ("single_party", "single-party"),
            ]:
                v = S[c][m]["role_classes"][cl]
                rows.append(
                    f"{lab} & {ml} & {cll} & {f3(v['share'])} & {f3(v['S1'])} & {f3(v['M5'])} & {f3(v['sponsor_bills'])} & {f3(v['sponsor_activity'])} & {f3(v['bills_null'])} & {f3(v['chance'])}"
                )
    table(
        "v3_role_classes.tex",
        "Top-1 accuracy on the role-assignment sets by number of original co-sponsors and coalition type.",
        "tab:role-classes",
        "lllrrrrrrr",
        [
            r"Case & mask & class & share & S1 & M5 & bill count & out-degree & bill-count draw & chance \\"
        ],
        rows,
        "With one original co-sponsor, role assignment asks which of two legislators filed the bill.",
        resize=True,
    )
    # covariate decomposition
    rows = []
    for m, ml in MECHS:
        for cl, cll in [("bipartisan", "bipartisan"), ("single_party", "single-party")]:
            v = D[m][cl]
            rows.append(
                f"{ml} & {cll} & {f3(v['S0']['mean'])} & "
                + " & ".join(
                    f"{f3(v[k]['gain_over_S0'][0])} [{f3(v[k]['gain_over_S0'][1])}, {f3(v[k]['gain_over_S0'][2])}]"
                    for k in ["S0+party", "S0+state", "S0+ideology", "S1"]
                )
            )
    table(
        "v3_decomposition.tex",
        "118th Senate: gain in concordance over S0 on the party-matched sets from each political covariate alone and from all three (S1).",
        "tab:decomposition",
        "llrllll",
        [r"Mask & coalition & S0 & $+$ party & $+$ state & $+$ ideology & S1 \\"],
        rows,
        "All models fitted by exact MLE with structural zeros. Brackets: 95\\% mask-bootstrap intervals. On party-matched sets both candidates have the same number of same-caucus arcs, so party matching can distinguish them only through Independents.",
        resize=True,
    )
    # sensitivity (third run)
    rows = []
    for c, lab in [("s118cap3", "head limit 3"), ("s118uncap", "training on all hyperarcs")]:
        for m, ml in MECHS:
            M = E[c][m]
            for k in [
                "M5",
                "M5_t05",
                "S1",
                "aa_total",
                "degprod",
                "weighted_footprint",
                "sponsor_bills",
            ]:
                rows.append(
                    f"{lab} & {ml} & {NAMES[k]} & "
                    + " & ".join(f3(M[s_][k]["concordance"][0]) for s_, _ in SETS)
                    + f" & {f3(M['role'][k]['top1'][0])}"
                )
            rows.append(
                f"{lab} & {ml} & chance & 0.500 & 0.500 & 0.500 & 0.500 & {f3(M['role']['chance']['top1'][0])}"
            )
    table(
        "v3_sensitivity.tex",
        "118th Senate, sensitivity analyses with the final estimators: concordance (R, P, H, S) and top-1 accuracy (A).",
        "tab:senate-limit-sensitivity",
        "lllrrrrr",
        [r"Analysis & mask & score & R & P & H & S & A \\"],
        rows,
        "Head limit 3: separately constructed target of hyperarcs with at most three original co-sponsors. Training on all hyperarcs: the training 2-section and the record counts also contain the hyperarcs above the head limit, which are never withheld.",
        resize=True,
    )
    # pooled PR-AUC (current run)
    rows = []
    for k in ["aa_total", "degprod", "weighted_footprint", "M5_t05", "M4c", "M5", "S0", "S1", "SI"]:
        cells = []
        for m, _ in MECHS:
            cells += [f3(S["s118"][m][s_][k]["pr_auc"][0]) for s_, _ in SETS]
        rows.append(NAMES[k] + " & " + " & ".join(cells))
    table(
        "v3_prauc.tex",
        "118th Senate: pooled PR-AUC (average precision over all candidates of a mask) for the final estimators.",
        "tab:prauc",
        "l" + "r" * 8,
        [
            r" & \multicolumn{4}{c}{MCAR} & \multicolumn{4}{c}{MNAR-out} \\",
            r"Score & R & P & H & S & R & P & H & S \\",
        ],
        rows,
        "Pooled PR-AUC compares candidates of different sizes and is a secondary metric; concordance is in Table~5 of the main text.",
    )
    # joint footprint scores
    rows = []
    for (_m, ml), Jm in zip(MECHS, J, strict=False):
        for key in ["M4c|random", "M4c|perturb", "M5|random", "M5|perturb"]:
            vals = [Jm[r][key] for r in Jm]
            import numpy as _np

            lj = _np.array([v["LJ"] for v in vals])
            l1 = _np.array([v["L1g"] for v in vals])
            mod, st = key.split("|")
            rows.append(
                f"{ml} & {mod} & {'random' if st == 'random' else 'head perturbation'} & {len(vals)} & {f3(lj.mean())} & {f3(l1.mean())} & {f3(_np.abs(lj - l1).max())}"
            )
    table(
        "v3_joint.tex",
        "118th Senate: within-pair concordance of the exact joint footprint score $L_J$ and of $L_{1g}$ for the degree-term models with the selected decay.",
        "tab:joint",
        "lllrrrr",
        [r"Mask & model & candidate set & masks & $L_J$ & $L_{1g}$ & max.\ $|$difference$|$ \\"],
        rows,
        "First ten masks of each mechanism. Within a pair both footprints have the same size, so normalization per arc does not change the comparison.",
    )
    print("extra SI tables written")
