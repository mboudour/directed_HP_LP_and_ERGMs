# CAVIAR direction and phase-label decision

The UCINET publisher describes Project Caviar as 11 directed, valued person-by-person phase matrices and one complete 110-by-110 matrix. It identifies the ties as police-wiretap communication exchanges and their values as communication activity. The page does not itself say whether an entry in row *i*, column *j* is a call from *i* to *j* or the reverse.[1]

A later peer-reviewed analysis of the same Project Caviar networks states explicitly that the directed links point **from caller to receiver** and that weights are the number of exchanged phone calls.[2] This is adequate to approve that orientation for the exact supplied full static matrix, but it does not repair a label-integrity defect in the phase series.

The local source audit finds that `CAVIAR_FULL.csv` has 110 unique labels. In contrast, `CAVIAR7.csv` has 37 positions but repeats actor label `9` in positions 9 and 15; its paired UCINET header repeats the same label. Because there is no source-level correction identifying the second actor, the phase series is retained unchanged but excluded from directed or temporal inference. The full matrix is approved only for static dyadic analysis.

**References**

[1]: https://sites.google.com/site/ucinetsoftware/datasets/covert-networks/caviar "Analytic Technologies CAVIAR dataset documentation"

[2]: https://www.mdpi.com/2078-2489/15/2/84 "Directed criminal networks temporal analysis and disruption"
