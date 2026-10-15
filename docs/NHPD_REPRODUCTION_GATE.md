# NHP-D reproduction gate

## Plan requirement

Section 9.5(4) of the agreed plan requires an NHP-D reproduction on one dataset
before a neural benchmark is added to the main comparison. If it cannot train
reliably, that outcome must be reported and the non-neural comparison remains
the primary benchmark.

## Official release inspected

The NHP article’s linked source archive was retrieved from the authors’ public
Google Drive link (file ID `1pgSPvv6Y23X5cPiShCpF4bU8eqz_34YE`) on 2026-10-15.
The file was `1,311,398` bytes with SHA-256
`5d3396c273ff976fd122a70e1661d6b92a78b3768d5ca5a1e43c77db7e0016ba`. Its README describes the release as
the source for the CIKM 2020 NHP paper.

The archive declares this frozen environment:

- `torch==1.1.0`
- `numpy==1.16.3`
- `scipy==1.2.1`
- `scikit_learn==0.21.1`

It contains an undirected `iAF1260b` dataset and preprocessing notebooks, but
no `reverb` directory or other bundled directed dataset, even though the
runtime loader names `reverb` as its directed case. Consequently, the release
does **not** provide a public packaged NHP-D reproduction dataset.

## Compatibility probe

A CPU probe used the project’s declared neural extra (PyTorch 2.14.1 and
current scikit-learn) without modifying any tracked project source.

1. The unmodified release fails before loading its published split because the
   command-line parser stores `--split` as a float and attempts to open
   `splits/1.0/indices.pkl`.
2. A **local, external, non-committed compatibility-only** change of that parser
to an integer allows the included undirected dataset to load. Training then
fails in the first epoch because the released model sends gradient-tracked Torch
tensors directly to `sklearn.metrics.roc_auc_score`; current Torch rejects
`Tensor.numpy()` on a tensor requiring gradients.
3. This probe is not an NHP-D result: the only bundled dataset is undirected,
and no official directed split is included.

## Gate decision

**NHP-D reproduction gate: not passed / no neural result admitted.**

The correct response is not to relabel a fresh architecture or a patched,
unpublished reimplementation as “NHP-D.” The present paper will retain its
predeclared non-neural dyadic, hyperarc, ERGM, and bounded-temporal comparisons.
A neural NHP-D comparison may be reconsidered only if a maintainable official
implementation and compatible directed input protocol become available, or if
a separately documented reimplementation is justified for a later study.

## Reproduction artifacts

- The source URL and SHA-256 are recorded in
  `data/metadata/gates/nhpd_reproduction.json`.
- The two terminal logs record the unmodified and compatibility-only probes.
- The exact paper source link is recovered from the PDF annotation, rather than
  from a third-party code mirror.
