# Enron address-level core-candidate profile

## Scope

This audit evaluates nested candidate cores. It does not select, export, or fit any core.

- Source nodes: `86,408`
- Source arcs: `360,402`
- Source native events: `490,141`

A node belongs to candidate core `k` if it has at least `k` distinct observed in-neighbors
and at least `k` distinct observed out-neighbors in the complete address-level graph.

| k | Nodes | Arcs | Density | Recip. pairs | Sender events | Full events | Recipient retention |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 10,456 | 196,416 | 0.001797 | 29,665 | 451,401 | 322,942 | 75.440% |
| 2 | 6,638 | 176,973 | 0.004017 | 27,588 | 432,346 | 285,749 | 72.250% |
| 5 | 4,163 | 148,726 | 0.008584 | 24,925 | 401,260 | 243,364 | 66.787% |
| 10 | 2,822 | 120,086 | 0.015085 | 22,051 | 383,049 | 209,885 | 60.743% |
| 20 | 1,774 | 85,664 | 0.027236 | 17,672 | 361,404 | 172,550 | 52.890% |
| 50 | 616 | 29,263 | 0.077244 | 8,018 | 296,340 | 94,946 | 34.217% |

## Interpretation

The table is a decision aid for reproducible core selection. “Full events” requires the
sender and every recipient of a native event to be in the candidate core; “recipient
retention” is less restrictive and counts recipient positions whose addresses remain in
the core. No threshold has been selected by this script.
