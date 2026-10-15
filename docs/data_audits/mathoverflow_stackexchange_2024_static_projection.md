# MathOverflow static projection and core preparation

- Approved reconstructed native events read: `91,161`
- Nodes in the full reconstructed-event view: `32,117`
- Full static directed arcs: `120,197`
- Core rule: top `100` by sent-plus-received reconstructed-event participation
- Core all-participant native events: `1,949`
- Core static directed arcs: `1,020`
- Core-size exception: `False`

The core retains only events whose answerer tail and asker head all belong to
its fixed activity-ranked node universe. The static graph is derived from this
same all-participant core-event view. These are reconstructed question-answer
events, not observed multi-recipient messages.
