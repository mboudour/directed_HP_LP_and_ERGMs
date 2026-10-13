# Dataset metadata

This directory stores tracked, non-sensitive metadata only: dataset manifests, source citations, licenses, transformation logs, and schema descriptions.

Before a dataset is used, create a provenance sheet in `docs/data_audits/` that records:

1. source and acquisition date;
2. raw record unit and event identifier;
3. direction semantics;
4. whether recipient bundles or other native group events are observed;
5. deduplication and node-resolution rules;
6. time coverage, access terms, and redistribution limits;
7. allowed targets: footprint, concept, native event, and role assignment.

Raw files belong in `data/raw/` or `data/external/` and must not be committed.
