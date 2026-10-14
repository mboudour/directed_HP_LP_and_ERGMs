# MathOverflow static projection and core protocol

The approved MathOverflow source is a 30-day reconstructed event table, not a
recorded multi-recipient communication log. The static projection therefore
retains the event-construction label throughout processing.

`make phase2-mathoverflow-static-prep` reads the approved native events and
creates the following local, ignored derived files:

- `static_arcs.parquet`: the full answerer → asker static directed graph with
  interaction counts;
- `core100_nodes.csv`: nodes ranked by sent-plus-received reconstructed-event
  participation, with stable node-ID tie breaks;
- `core100_native_events.parquet`: only events whose complete tail and head lie
  in the fixed core; and
- `core100_static_arcs.parquet`: arcs induced by those same all-participant
  core events.

Using all-participant events for both native-event and static core views avoids
leakage from an outside answerer into a nominally core-only event. The static
view is ready for the cap-first concept audit only after its count and
core-size report are reviewed.

Run:

```bash
make phase2-mathoverflow-static-prep
```
