# Network Science political-networks manuscript package

This directory contains the Network Science special-collection version of the manuscript, built around the completed 118th U.S. Senate co-sponsorship application. It uses the official `nws.cls` file supplied with the Network Science author template; the supplied `nwslike.bst` is retained with the package, while the source uses stable author--date `plainnat` BibTeX output pending copy-editing by the journal.

## Submission files

- `Paper1_NetworkScience.tex` is the anonymized main document for double-blind review. It contains no author name, affiliation, e-mail address, acknowledgements, or repository URL.
- `Paper1_NetworkScience.bib` is the verified BibTeX database used by the main document.
- `TitlePage_NetworkScience.tex` is the separate, non-anonymized title page. Do not include it in the main-document upload.
- `figures/` contains source-controlled, aggregate-only figures.
- `tables/` contains TeX fragments generated from aggregate-only evidence.
- `nws.cls`, `nwslike.bst`, and `cup_logo.pdf` are the relevant official-template files.

## Reproducible build

From the repository root, run:

```sh
make manuscript-network-science
```

The target regenerates the Senate aggregate evidence bundle, manuscript tables, and quantitative figures, then compiles both PDFs into `manuscript/network_science/build/`.

For a downloaded, self-contained source package, the simplest reliable command is:

```sh
bash compile_network_science.sh
```

Run it from the directory containing this README. It creates
`build/Paper1_NetworkScience.pdf` and applies the required `pdflatex`,
`bibtex`, `pdflatex`, `pdflatex` sequence. The source-level manual sequence
for the anonymized main document is:

```sh
cd manuscript/network_science
rm -rf build && mkdir build
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Paper1_NetworkScience.tex
cp Paper1_NetworkScience.bib build/
(cd build && bibtex Paper1_NetworkScience)
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Paper1_NetworkScience.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Paper1_NetworkScience.tex
```

The compiled PDF has placeholder journal metadata (`1--1` and `doi: to be assigned`), which is normal in a pre-submission manuscript using the journal class.

## Evidence and scope

The primary political evidence is the cap-ten native-event benchmark for Senate bills with a sole sponsor and nonempty original-co-sponsor head. The methods use controlled MCAR and activity-biased oracle omission (MNAR-out) of full recorded event types; these are stress tests, not claims about natural archival missingness. Each synthetic random negative is paired to its held-out event type and requires every participant to be serving on every associated bill-introduction date under half-open Senate-term intervals. Reported bootstrap intervals resample the 30 matched masks within the fixed constructed Senate network; they are not population-level uncertainty intervals. ERGM rows are split-specific MPLE conditional scores and factorized footprint summaries, never estimates of a joint coalition probability.

Raw or private data, actor-level event tables, prediction-level candidates, fitted objects, and sensitive e-mail material are deliberately excluded from this package and from repository publication.
