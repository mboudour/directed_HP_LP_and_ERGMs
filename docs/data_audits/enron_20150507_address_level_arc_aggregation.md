# Enron address-level directed-arc aggregation

## Scope

The address-level native events are aggregated into a directed graph. An arc exists for
every sender-recipient pair observed in one or more retained native events. The Parquet
output remains local because it contains addresses.

- Native events read: `490,141`
- Event-to-arc occurrences: `3,608,724`
- Unique address-level nodes: `86,408`
- Unique directed arcs: `360,402`
- Self arcs: `0`
- Reciprocal unordered pairs: `29,665`
- Directed density, excluding loops:
  `0.00004827`

## Aggregation rule

Each event contributes one arc from its sender to every address in its To-plus-Cc head.
Arc weights equal the number of retained native events containing that ordered dyad.
This creates the address-level graph only; it does not resolve aliases or choose the
smaller core graph used for concept enumeration and ERGM estimation.
