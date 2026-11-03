# ruff: noqa: E501
"""Write the main-text tables of the second benchmark run (within-pair metrics, exact p1 MLE).

Usage: python make_tables_v2.py SUMMARY_V2_JSON COEF_JSON CLOSURE_JSON TABLES_DIR
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
    "observed_fraction": "observed footprint share",
    "party_share": "same-party share",
    "M4c": "M4c (MPLE)",
    "M5": "M5 (MPLE)",
    "M6": "M6 (MPLE)",
    "S0mle": "S0 (MLE)",
    "S1mle": "S1 (MLE)",
    "S1": "S1 (MPLE)",
    "chance": "chance",
}


def f3(x):
    return f"{x:.3f}".replace("-0.000", "0.000")


def pv(p):
    return "$<0.0001$" if p < 1e-4 else f"{p:.4f}"


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


# ------------------------------------------------------------ Table: 118th Senate performance
rows = []
for k in [
    "aa_total",
    "aa_oi",
    "degprod",
    "sponsor_activity",
    "sponsor_bills",
    "observed_fraction",
    "party_share",
    "M4c",
    "M5",
    "M6",
    "S0mle",
    "S1mle",
]:
    cells = []
    for mech, _ in MECHS:
        M = S["s118"][mech]
        cells += [f3(M[s][k]["concordance"][0]) for s in ("random", "matched", "sub")]
        cells.append(f3(M["role"][k]["top1"][0]))
    rows.append(NAMES[k] + " & " + " & ".join(cells))
ch = [f3(S["s118"][m]["role"]["chance"]["top1"][0]) for m, _ in MECHS]
rows.append(f"chance & 0.500 & 0.500 & 0.500 & {ch[0]} & 0.500 & 0.500 & 0.500 & {ch[1]}")
table(
    "v2_performance.tex",
    "118th Senate: mean within-pair concordance on the random (R), party-matched (P) and substitution (S) candidate sets, and top-1 accuracy on the role-assignment sets (A), over 30 masks per mechanism.",
    "tab:senate-performance",
    "lrrrrrrrr",
    [
        r" & \multicolumn{4}{c}{MCAR} & \multicolumn{4}{c}{MNAR-out} \\",
        r"Score & R & P & S & A & R & P & S & A \\",
    ],
    rows,
    "Concordance is the share of pairs in which the recorded hyperarc scores above its alternative (ties count one half). "
    "Model scores are $L_{1g}$ from fits to the training 2-section; local scores are footprint averages (Section~4.1). "
    "Pooled PR-AUC values are in Supplementary Table~S4.",
    resize=True,
)


# ------------------------------------------------------------ Table: 118th Senate contrasts
def cell(c, tl):
    return f"{f3(c[0])} & [{f3(tl[0])}, {f3(tl[1])}]"


rows = []
for mech, lab in MECHS:
    M = S["s118"][mech]
    for s, slab in [("random", "R"), ("matched", "P"), ("sub", "S")]:
        for x, y in [
            ("S1mle", "M5"),
            ("S1mle", "aa_total"),
            ("S1mle", "degprod"),
            ("S1mle", "sponsor_bills"),
            ("S1mle", "S0mle"),
        ]:
            v = M[s + "_contrasts"][f"{x} - {y}"]
            rows.append(
                f"{lab} & {slab} & {NAMES[x]} $-$ {NAMES[y]} & "
                + cell(v["concordance"], v["concordance_two_level"])
            )
    for x, y in [
        ("S1mle", "chance"),
        ("S1mle", "aa_oi"),
        ("S1mle", "degprod"),
        ("S1mle", "sponsor_bills"),
        ("M6", "chance"),
    ]:
        v = M["role_contrasts"][f"{x} - {y}"]
        rows.append(
            f"{lab} & A & {NAMES[x]} $-$ {NAMES[y]} & " + cell(v["top1"], v["top1_two_level"])
        )
table(
    "v2_contrasts.tex",
    "118th Senate: paired contrasts of concordance (R, P, S) and of top-1 accuracy (A).",
    "tab:senate-contrasts",
    "lllrl",
    [r"Mask & set & contrast & difference & 95\% interval \\"],
    rows,
    "Differences are means over 30 masks. Intervals are two-level bootstrap intervals that resample masks and, within each mask, "
    "the evaluated hyperarcs; they are wider than the mask-only intervals of Monte Carlo precision.",
)

# ------------------------------------------------------------ Table: bipartisan
rows = []
for mech, lab in MECHS:
    M = S["s118"][mech]
    for s, slab in [("random", "random"), ("matched", "party-matched")]:
        for cl, cll in [("bipartisan", "bipartisan"), ("single_party", "single-party")]:
            v = M[s + "_classes"][cl]
            a = v["contrasts"]["M5 - M4c"]
            b = v["contrasts"]["S1mle - S0mle"]
            rows.append(
                f"{lab} & {slab} & {cll} & {f3(v['share'])} & {f3(v['concordance']['party_share'])} & "
                f"{f3(a[0])} [{f3(a[1])}, {f3(a[2])}] & {f3(b[0])} [{f3(b[1])}, {f3(b[2])}]"
            )
table(
    "v2_bipartisan.tex",
    "118th Senate: effect of the political covariates on concordance, by coalition type and candidate set.",
    "tab:bipartisan",
    "llllrll",
    [r"Mask & candidate set & coalition & share & same-party share & M5 $-$ M4c & S1 $-$ S0 \\"],
    rows,
    "A hyperarc is bipartisan if at least one original co-sponsor belongs to another caucus than the sponsor; Independents belong to the "
    "Democratic caucus. Party-matched alternatives have an initiator of the sponsor's caucus and the same number of co-sponsors from each caucus. "
    "S1 and S0 are fitted by maximum likelihood. Brackets: 95\\% mask-bootstrap intervals.",
    resize=True,
)

# ------------------------------------------------------------ Table: four cases
rows = []
items = [
    ("S1 $-$ directed AA, R", lambda M: M["random_contrasts"]["S1mle - aa_total"]["concordance"]),
    ("S1 $-$ M5, P", lambda M: M["matched_contrasts"]["S1mle - M5"]["concordance"]),
    ("S1 $-$ directed AA, P", lambda M: M["matched_contrasts"]["S1mle - aa_total"]["concordance"]),
    ("S1 $-$ degree product, S", lambda M: M["sub_contrasts"]["S1mle - degprod"]["concordance"]),
    (
        "S1 $-$ initiator bill count, S",
        lambda M: M["sub_contrasts"]["S1mle - sponsor_bills"]["concordance"],
    ),
    ("S1 top-1 $-$ chance, A", lambda M: M["role_contrasts"]["S1mle - chance"]["top1"]),
    (
        "S1 $-$ initiator out-degree, A",
        lambda M: M["role_contrasts"]["S1mle - sponsor_activity"]["top1"],
    ),
    ("S1 $-$ Adamic--Adar two-paths, A", lambda M: M["role_contrasts"]["S1mle - aa_oi"]["top1"]),
    ("M6 top-1 $-$ chance, A", lambda M: M["role_contrasts"]["M6 - chance"]["top1"]),
    (
        "S1 $-$ S0, P, bipartisan",
        lambda M: M["matched_classes"]["bipartisan"]["contrasts"]["S1mle - S0mle"],
    ),
    (
        "S1 $-$ S0, P, single-party",
        lambda M: M["matched_classes"]["single_party"]["contrasts"]["S1mle - S0mle"],
    ),
]
for lab, fn in items:
    cells = []
    for c, _ in CASES:
        for m, _ in MECHS:
            v = fn(S[c][m])
            cells.append(f3(v[0]))
    rows.append(lab + " & " + " & ".join(cells))
table(
    "v2_cases.tex",
    "Main contrasts in all four cases: mean differences over 30 masks in concordance (R, P, S) or top-1 accuracy (A).",
    "tab:case-results",
    "l" + "r" * 8,
    [
        r" & \multicolumn{2}{c}{118th Senate} & \multicolumn{2}{c}{117th Senate} & \multicolumn{2}{c}{116th Senate} & \multicolumn{2}{c}{118th House} \\",
        r"Contrast & MCAR & MNAR & MCAR & MNAR & MCAR & MNAR & MCAR & MNAR \\",
    ],
    rows,
    "R, P, S, A: random, party-matched, substitution and role-assignment candidate sets. S0 and S1 are fitted by maximum likelihood. "
    "Supplementary Table~S3 gives intervals.",
    resize=True,
)

# ------------------------------------------------------------ Table: coefficients
rows = []
for c, lab in CASES:
    r = C[c]
    m5, s1 = r["M5_mple"], r["S1_mle"]
    reg = r["S1_sender_regression"]
    rows.append(
        f"{lab} & {f3(m5['mutual'])} & {f3(m5['nodematch_party'])} & {f3(m5['nodematch_state'])} & {f3(m5['absdiff_nominate'])} & "
        f"{f3(s1['mutual'])} & {f3(s1['nodematch_party'])} & {f3(s1['nodematch_state'])} & {f3(s1['absdiff_nominate'])} & "
        f"{f3(r['S1_mle_actor_sd']['sender'])} & {f3(reg['r2_majority_seniority'])} & {f3(reg['corr_log_bills'])}"
    )
table(
    "v2_coefficients.tex",
    "Coefficients on the complete 2-section of eligible hyperarcs: M5 (MPLE) and S1 (exact MLE).",
    "tab:coefficients",
    "l" + "r" * 11,
    [
        r" & \multicolumn{4}{c}{M5} & \multicolumn{4}{c}{S1} & \multicolumn{3}{c}{S1 sender effects} \\",
        r"Case & mutual & party & state & ideology & mutual & party & state & ideology & SD & $R^2$ & $r$ \\",
    ],
    rows,
    "Party and state: matching; ideology: absolute difference in first-dimension DW-NOMINATE. Party matching distinguishes Independents from Democrats. "
    "SD: standard deviation of the sender effects of actors with at least one arc. $R^2$: share of their variance explained by majority-caucus membership "
    "and seniority. $r$: correlation with the logarithm of one plus the number of eligible bills sponsored. Standard errors are omitted; "
    "coefficients describe the fitted models and are not interpreted causally.",
    resize=True,
)

# ------------------------------------------------------------ Table: concept closure
rows = []
for c, lab in CASES:
    k = K[c]
    rows.append(
        f"{lab} & {k['hyperarcs']:,} & {f3(k['share_equal_head_concept'])} & {k['mean_tail_size_head_concept']:.1f} & "
        f"{f3(k['mean_head_ratio'])} & {f3(k['mean_footprint_jaccard'])} & {f3(k['mean_head_over_outneighbourhood'])}"
    )
table(
    "v2_closure.tex",
    "Recorded hyperarcs and the formal concepts they generate in the 2-section of all recorded hyperarcs, without size limits.",
    "tab:closure",
    "lrrrrrr",
    [
        r"Case & hyperarcs & equal to concept & $|H^{\downarrow}|$ & $|H|/|H^{\downarrow\uparrow}|$ & Jaccard & $|H|/|N^+(s)|$ \\"
    ],
    rows,
    "For a hyperarc $(\\{s\\},H)$ the generated concept is $(H^{\\downarrow},H^{\\downarrow\\uparrow})$, the smallest concept whose head contains $H$. "
    "Columns give the share of hyperarcs equal to their generated concept and means over hyperarcs of the size of its tail, of the head ratio, "
    "of the Jaccard similarity of the two footprints, and of the head size relative to the sponsor's out-neighbourhood.",
    resize=True,
)
print("v2 tables written")

# ------------------------------------------------------------ SI: case contrasts with intervals
rows = []
for c, lab in CASES:
    for m, ml in MECHS:
        M = S[c][m]
        for name, (setk, key, tlkey) in [
            ("S1 $-$ directed AA, R", ("random_contrasts", "S1mle - aa_total", "concordance")),
            (
                "S1 $-$ observed share, R",
                ("random_contrasts", "S1mle - observed_fraction", "concordance"),
            ),
            ("S1 $-$ M5, P", ("matched_contrasts", "S1mle - M5", "concordance")),
            ("S1 $-$ degree product, S", ("sub_contrasts", "S1mle - degprod", "concordance")),
            ("S1 $-$ chance, A", ("role_contrasts", "S1mle - chance", "top1")),
            (
                "S1 $-$ initiator out-degree, A",
                ("role_contrasts", "S1mle - sponsor_activity", "top1"),
            ),
            ("M6 $-$ chance, A", ("role_contrasts", "M6 - chance", "top1")),
        ]:
            v = M[setk][key]
            tl = v[tlkey + "_two_level"]
            mc = v[tlkey]
            rows.append(
                f"{lab} & {ml} & {name} & {f3(mc[0])} & [{f3(mc[1])}, {f3(mc[2])}] & [{f3(tl[0])}, {f3(tl[1])}]"
            )
table(
    "v2_cases_ci.tex",
    "Main contrasts in all four cases with mask-bootstrap and two-level bootstrap intervals.",
    "tab:case-ci",
    "llllll",
    [r"Case & mask & contrast & difference & masks & masks and hyperarcs \\"],
    rows,
    "R, P, S, A: random, party-matched, substitution and role-assignment candidate sets; concordance for R, P, S and top-1 accuracy for A. S1 is fitted by maximum likelihood.",
    resize=True,
)

# ------------------------------------------------------------ SI: covariate effects by head size
rows = []
for m, ml in MECHS:
    M = S["s118"][m]
    for s_, sl in [("random", "random"), ("matched", "party-matched")]:
        for cl, cll in [
            ("bipartisan_size_1_3", "bipartisan, 1--3"),
            ("single_party_size_1_3", "single-party, 1--3"),
            ("bipartisan_size_4_10", "bipartisan, 4--10"),
            ("single_party_size_4_10", "single-party, 4--10"),
            ("bipartisan_20", "at least 20\\% other caucus"),
        ]:
            v = M[s_ + "_classes"][cl]
            a = v["contrasts"]["M5 - M4c"]
            b = v["contrasts"]["S1mle - S0mle"]
            rows.append(
                f"{ml} & {sl} & {cll} & {f3(v['share'])} & {f3(a[0])} [{f3(a[1])}, {f3(a[2])}] & {f3(b[0])} [{f3(b[1])}, {f3(b[2])}]"
            )
table(
    "v2_size_classes.tex",
    "118th Senate: effect of the political covariates on concordance by coalition type and number of original co-sponsors.",
    "tab:size-classes",
    "llllll",
    [r"Mask & candidate set & class & share & M5 $-$ M4c & S1 $-$ S0 \\"],
    rows,
    "The last class uses a share-based definition: at least 20\\% of the original co-sponsors belong to another caucus than the sponsor. Brackets: 95\\% mask-bootstrap intervals.",
    resize=True,
)

# ------------------------------------------------------------ SI: MLE versus MPLE
rows = []
for c, lab in CASES:
    r = C[c]
    for mname in ["S0", "S1"]:
        a, b = r[mname + "_mle"], r[mname + "_mple"]
        inf = r[mname + "_mle_info"]
        terms = [
            t
            for t in a
            if t in ("edges", "mutual", "nodematch_party", "nodematch_state", "absdiff_nominate")
        ]
        diff = max(abs(a[t] - b[t]) for t in terms)
        rows.append(
            f"{lab} & {mname} & {inf['observed_arcs']:,} & {inf['expected_arcs']:.3f} & {inf['observed_mutual']:,} & {inf['expected_mutual']:.3f} & {f3(diff)}"
        )
    for m, ml in MECHS:
        d = S[c][m]["random_contrasts"]["S1mle - S1"]["concordance"]
        rows.append(
            f"{lab} & S1 masks, {ml} & \\multicolumn{{4}}{{l}}{{concordance MLE $-$ MPLE, random set}} & {f3(d[0])}"
        )
table(
    "v2_mle.tex",
    "Exact maximum likelihood for S0 and S1: score equations on the complete 2-section and agreement with MPLE.",
    "tab:mle-mple",
    "llrrrrr",
    [
        r"Case & model & arcs & expected & mutual & expected & max.\ $|\hat\theta_{\mathrm{MLE}}-\hat\theta_{\mathrm{MPLE}}|$ \\"
    ],
    rows,
    "Expected counts are computed under the fitted model; at the MLE they equal the observed counts. The last column compares the coefficients of the arc, "
    "mutuality and covariate terms. Rows labelled masks give the mean difference in concordance between MLE and MPLE fits of S1 over 30 masks.",
    resize=True,
)
print("v2 SI tables written")
