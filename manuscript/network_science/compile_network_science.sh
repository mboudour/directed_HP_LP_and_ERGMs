#!/usr/bin/env bash
# Build the anonymized Network Science manuscript from this complete source folder.
# Usage: bash compile_network_science.sh
set -euo pipefail

cd "$(dirname "$0")"

for command in pdflatex bibtex; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf 'Required TeX command is unavailable: %s\n' "$command" >&2
    exit 127
  fi
done

rm -rf build
mkdir -p build

pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=build Paper1_NetworkScience.tex
cp Paper1_NetworkScience.bib build/
(
  cd build
  bibtex Paper1_NetworkScience
)
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=build Paper1_NetworkScience.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=build Paper1_NetworkScience.tex

printf 'Built: %s/build/Paper1_NetworkScience.pdf\n' "$PWD"
