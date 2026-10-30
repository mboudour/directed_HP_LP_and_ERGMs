#!/usr/bin/env python3
"""Prepare audited Enron native events for a directed-RHEM case-control pilot.

The source is the existing custodian-level native-event projection.  This driver
never edits that source or the static Paper 1 projection.  It emits an ignored,
pseudonymized Eventnet input bundle and safe aggregate readiness records.

Each input email is one directed hyperevent with a singleton source and an
unordered, nonempty target set.  Eventnet represents the target set through
one CSV row per source--target incidence sharing an event-interval identifier.
The Eventnet configuration uses conditional-size case-control observations and
emits both a full event-choice and a receiver-set-given-sender candidate panel.

The archive contains many distinct native records sharing a timestamp.  The
source policy retains such records.  Eventnet's EVENT_INTERVAL semantics update
history after every event interval, so this driver makes the within-timestamp
order explicit and supports ascending and descending stable-ID sensitivity
bundles.  Neither order is treated as substantively privileged.
"""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "processed" / "enron_20150507" / "custodian_native_events.parquet"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "models" / "enron_temporal_rhem_inputs"
DEFAULT_AUDIT_JSON = PROJECT_ROOT / "data" / "metadata" / "enron_temporal_hyperevent_readiness.json"
DEFAULT_AUDIT_REPORT = (
    PROJECT_ROOT / "docs" / "data_audits" / "enron_temporal_hyperevent_readiness.md"
)

EVENTNET_FILE = "enron_events_eventnet.csv"
EVENTNET_CONFIG = "enron_rhem_config.xml"
ACTOR_MAP_FILE = "actor_map_private.csv"
EVENT_INDEX_FILE = "event_index_private.csv"
ROLLING_FOLDS_FILE = "rolling_folds_private.csv"
MANIFEST_FILE = "rhem_input_manifest.json"


def parse_args() -> argparse.Namespace:
    """Parse explicit Paper 2 RHEM-preparation options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Custodian native-event Parquet input.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="New ignored local Eventnet input bundle.",
    )
    parser.add_argument(
        "--tie-order",
        choices=("event_id_ascending", "event_id_descending"),
        default="event_id_ascending",
        help="Stable within-timestamp Eventnet interval ordering for sensitivity analysis.",
    )
    parser.add_argument(
        "--controls-per-event",
        type=int,
        default=20,
        help="Case controls sampled per observed event in each Eventnet observation.",
    )
    parser.add_argument(
        "--halflife-seconds",
        type=int,
        default=604_800,
        help="History-statistic exponential-decay half-life in seconds (default: 7 days).",
    )
    parser.add_argument(
        "--eventnet-random-seed",
        type=int,
        default=20261030,
        help="Nonnegative Eventnet XML seed for reproducible case-control sampling.",
    )
    parser.add_argument(
        "--core-size",
        type=int,
        default=50,
        help="Actor-universe size selected using history before --core-selection-origin.",
    )
    parser.add_argument(
        "--core-selection-origin",
        default="2001-01-01T00:00:00+00:00",
        help="UTC origin before which actor activity selects the frozen RHEM universe.",
    )
    parser.add_argument(
        "--evaluation-end",
        default="2002-01-01T00:00:00+00:00",
        help="Exclusive UTC endpoint for the predeclared 2001 expanding-fold evaluation.",
    )
    parser.add_argument(
        "--collapse-same-timestamp-footprints",
        action="store_true",
        help=(
            "Sensitivity only: retain one stable-ID record per identical timestamp, sender, and "
            "receiver-set footprint after actor selection."
        ),
    )
    parser.add_argument(
        "--audit-json",
        type=Path,
        default=DEFAULT_AUDIT_JSON,
        help="Safe aggregate JSON readiness audit.",
    )
    parser.add_argument(
        "--audit-report",
        type=Path,
        default=DEFAULT_AUDIT_REPORT,
        help="Safe aggregate Markdown readiness audit.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the named output bundle and aggregate audit records.",
    )
    args = parser.parse_args()
    if args.controls_per_event < 1:
        parser.error("--controls-per-event must be positive.")
    if args.halflife_seconds < 1:
        parser.error("--halflife-seconds must be positive.")
    if args.eventnet_random_seed < 0:
        parser.error("--eventnet-random-seed must be nonnegative.")
    if args.core_size < 2:
        parser.error("--core-size must be at least two.")
    return args


def resolve(path: Path) -> Path:
    """Resolve a potentially project-relative path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Record a path relative to the repository whenever possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 digest for provenance."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_utc(value: str, *, option: str) -> datetime:
    """Parse a timezone-aware ISO datetime for an explicit temporal boundary."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise SystemExit(f"STOP: {option} must be an ISO UTC datetime: {value!r}") from error
    if parsed.tzinfo is None:
        raise SystemExit(f"STOP: {option} must include a timezone: {value!r}")
    return parsed.astimezone(UTC)


def read_events(path: Path) -> list[dict[str, Any]]:
    """Read and validate the minimal native-event contract."""
    if not path.is_file():
        raise SystemExit(f"STOP: native-event input is missing: {path}")
    source = pq.ParquetFile(path)
    required = {"event_id", "sent_at_utc", "tail_custodian", "head_custodians"}
    missing = required - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: native-event input lacks columns {sorted(missing)}: {path}")

    events: list[dict[str, Any]] = []
    for batch in source.iter_batches(columns=sorted(required), batch_size=20_000):
        for row in batch.to_pylist():
            event_id = str(row["event_id"]).strip()
            tail = str(row["tail_custodian"]).strip()
            timestamp = row["sent_at_utc"]
            head_values = row["head_custodians"]
            if not event_id or not tail:
                raise SystemExit("STOP: native-event input has a blank event ID or sender.")
            if not isinstance(timestamp, datetime) or timestamp.tzinfo is None:
                raise SystemExit("STOP: native-event input needs timezone-aware timestamps.")
            if not isinstance(head_values, list):
                raise SystemExit("STOP: native-event input has a non-list receiver set.")
            head = tuple(
                sorted({str(value).strip() for value in head_values if str(value).strip()})
            )
            if not head:
                raise SystemExit("STOP: native-event input includes an empty receiver set.")
            if tail in head:
                raise SystemExit("STOP: native-event input includes a sender in its receiver set.")
            events.append(
                {
                    "event_id": event_id,
                    "timestamp": timestamp.astimezone(UTC),
                    "tail": tail,
                    "head": head,
                }
            )
    if len(events) < 2:
        raise SystemExit("STOP: temporal RHEM preparation needs at least two native events.")
    if len({event["event_id"] for event in events}) != len(events):
        raise SystemExit("STOP: native-event input has duplicate event IDs.")
    return events


def order_events(events: list[dict[str, Any]], tie_order: str) -> list[dict[str, Any]]:
    """Order events chronologically with an explicit within-timestamp sensitivity rule."""
    by_time: dict[datetime, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_time[event["timestamp"]].append(event)
    ordered: list[dict[str, Any]] = []
    reverse = tie_order == "event_id_descending"
    for timestamp in sorted(by_time):
        ordered.extend(
            sorted(by_time[timestamp], key=lambda row: str(row["event_id"]), reverse=reverse)
        )
    return ordered


def select_origin_safe_core(
    events: list[dict[str, Any]],
    *,
    core_size: int,
    selection_origin: datetime,
    evaluation_end: datetime,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Freeze an actor universe using only pre-origin participation.

    An actor's activity is one sender or receiver appearance in a native event.
    The lexical identifier is used only as a deterministic tie-break after the
    pre-origin count.  Events are retained only when every participant belongs
    to the selected universe, preventing a future-active actor from entering the
    risk set through full-period activity ranking.
    """
    if evaluation_end <= selection_origin:
        raise SystemExit("STOP: --evaluation-end must be after --core-selection-origin.")
    participation: Counter[str] = Counter()
    for event in events:
        if event["timestamp"] < selection_origin:
            participation[event["tail"]] += 1
            participation.update(event["head"])
    if len(participation) < core_size:
        raise SystemExit(
            "STOP: fewer pre-origin active actors than --core-size: "
            f"{len(participation):,} < {core_size:,}."
        )
    selected = tuple(
        actor
        for actor, _ in sorted(participation.items(), key=lambda item: (-item[1], item[0]))[
            :core_size
        ]
    )
    selected_set = set(selected)
    retained = [
        event
        for event in events
        if event["timestamp"] < evaluation_end
        and event["tail"] in selected_set
        and set(event["head"]).issubset(selected_set)
    ]
    pre_origin_retained = sum(event["timestamp"] < selection_origin for event in retained)
    if pre_origin_retained < 2:
        raise SystemExit("STOP: frozen actor universe leaves fewer than two pre-origin events.")
    return retained, {
        "method": "pre_origin_participation_rank",
        "core_size": core_size,
        "selection_origin_utc": selection_origin.isoformat(),
        "evaluation_end_utc_exclusive": evaluation_end.isoformat(),
        "pre_origin_events_before_participant_filter": sum(
            event["timestamp"] < selection_origin for event in events
        ),
        "pre_origin_active_actors": len(participation),
        "pre_origin_retained_events": pre_origin_retained,
        "retained_events_before_evaluation_end": len(retained),
        "actor_ids_private": list(selected),
    }


def collapse_same_timestamp_footprints(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Retain one deterministic representative of each identical time-role footprint.

    This is an explicitly labelled sensitivity for temporal event-process
    analysis. The primary input preserves the project-approved distinct source
    record policy, so this function is never called unless requested.
    """
    grouped: dict[tuple[datetime, str, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped[(event["timestamp"], event["tail"], event["head"])].append(event)
    collapsed = [min(group, key=lambda event: str(event["event_id"])) for group in grouped.values()]
    return collapsed, len(events) - len(collapsed)


def rolling_folds(events: list[dict[str, Any]], selection_origin: datetime) -> list[dict[str, Any]]:
    """Create the predeclared four expanding 2001 quarterly evaluation folds."""
    boundaries = (
        selection_origin,
        datetime(2001, 4, 1, tzinfo=UTC),
        datetime(2001, 7, 1, tzinfo=UTC),
        datetime(2001, 10, 1, tzinfo=UTC),
        datetime(2002, 1, 1, tzinfo=UTC),
    )
    if selection_origin != boundaries[0]:
        raise SystemExit(
            "STOP: the predeclared rolling folds require --core-selection-origin="
            "2001-01-01T00:00:00+00:00."
        )
    folds: list[dict[str, Any]] = []
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:], strict=False), start=1):
        folds.append(
            {
                "fold": f"2001_q{index}",
                "train_end_utc_exclusive": start.isoformat(),
                "test_start_utc_inclusive": start.isoformat(),
                "test_end_utc_exclusive": end.isoformat(),
                "training_events": sum(event["timestamp"] < start for event in events),
                "test_events": sum(start <= event["timestamp"] < end for event in events),
            }
        )
    if any(fold["training_events"] < 1 or fold["test_events"] < 1 for fold in folds):
        raise SystemExit(
            "STOP: one or more predeclared expanding folds is empty after actor filtering."
        )
    return folds


def eventnet_config(
    controls_per_event: int, halflife_seconds: int, eventnet_random_seed: int
) -> str:
    """Render a minimal documented directed-RHEM Eventnet configuration.

    The two observations share exactly the same sampled-risk-set construction.
    ``FULL_EVENT`` evaluates sender-plus-target-set choice conditional on target
    size. ``CONDITIONAL_SENDER_SET`` additionally conditions on the observed
    sender and therefore targets receiver-set recovery for a known sender.
    """
    return f'''<?xml version="1.0" ?>
<eventnet.configuration name="enron.temporal.rhem" version="1.1" random.seed="{eventnet_random_seed}">
  <input.files accept=".csv" has.header="true" delimiter="COMMA" quote.char="DOUBLEQUOTE">
    <input.directory name="."/>
    <file name="{EVENTNET_FILE}"/>
  </input.files>
  <output.directory name="eventnet_output"/>
  <event.components>
    <component name="SOURCE" column.name="sender"/>
    <component name="TARGET" column.name="receiver"/>
    <component name="TIME" column.name="time"/>
    <component name="TYPE" column.name="type"/>
    <component name="WEIGHT" column.name="weight"/>
    <component name="EVENT_INTERVAL_ID" column.name="event_interval_id"/>
  </event.components>
  <network.mode is.multimode="false"/>
  <event.types>
    <type name="add.actor" implied="false" admits.loops="true"/>
    <type name="email" implied="false" admits.loops="false"/>
  </event.types>
  <time time.format.type="INTEGER" interval.type="EVENT_INTERVAL" time.unit="1"/>
  <attribute name="at.risk" class="NODE_LEVEL" type="DEFAULT_NODE_LEVEL_ATTRIBUTE" description="">
    <attr.update type="SET_VALUE_TO"/>
    <event.response event.type="add.actor" direction="OUT"/>
  </attribute>
  <attribute name="emails" class="DIR_HYPER_LEVEL" type="DEFAULT_DHE_ATTRIBUTE" description="">
    <attr.update type="INCREMENT_VALUE_BY" decay.time.scale="TIME_UNIT" halflife="{halflife_seconds}.0"/>
    <event.response event.type="email"/>
  </attribute>
  <attribute name="emails.dyadic" class="DYAD_LEVEL" type="DYAD_LEVEL_ATTRIBUTE_FROM_DHE" description="">
    <attr.update type="INCREMENT_VALUE_BY" decay.time.scale="TIME_UNIT" halflife="{halflife_seconds}.0"/>
    <event.response event.type="email"/>
  </attribute>
  <statistic name="exact_rep" type="DHE_REPETITION_STAT" direction.1="OUT" hyperedge.attr.name.1="emails"/>
  <statistic name="dyad_rep" type="DHE_SUB_REPETITION_STAT" direction.1="OUT" hyperedge.attr.name.1="emails" source.size="1" target.size="1">
    <aggregation.function type="AVERAGE"/>
  </statistic>
  <statistic name="reciprocation" type="DHE_SUB_REPETITION_STAT" direction.1="IN" hyperedge.attr.name.1="emails" source.size="1" target.size="1">
    <aggregation.function type="AVERAGE"/>
  </statistic>
  <statistic name="target_pair_rep" type="DHE_SUB_REPETITION_STAT" direction.1="OUT" hyperedge.attr.name.1="emails" source.size="0" target.size="2" endpoint="TARGET">
    <aggregation.function type="AVERAGE"/>
  </statistic>
  <statistic name="receiver_interaction" type="DHE_SUB_REPETITION_STAT" direction.1="OUT" hyperedge.attr.name.1="emails" source.size="1" target.size="2" endpoint="TARGET">
    <aggregation.function type="AVERAGE"/>
  </statistic>
  <statistic name="transitive_closure" type="DHE_CLOSURE_STAT" dyad.attr.name.1="emails.dyadic" direction.1="OUT" dyad.attr.name.2="emails.dyadic" direction.2="IN">
    <function.combine.parallel type="SUM"/>
    <function.combine.serial type="MIN"/>
    <aggregation.function type="AVERAGE"/>
  </statistic>
  <observation name="FULL_EVENT" type="COND_SIZE_DHE_OBS" exclude.loops="true" apply.case.control.sampling="true" number.of.non.events="{controls_per_event}" non.events.are.per.observed.event="true" source.is.non.zero.on.attr="at.risk" target.is.non.zero.on.attr="at.risk">
    <consider.event.type name="email"/>
  </observation>
  <observation name="CONDITIONAL_SENDER_SET" type="COND_SIZE_DHE_OBS" exclude.loops="true" apply.case.control.sampling="true" number.of.non.events="{controls_per_event}" non.events.are.per.observed.event="true" source.is.non.zero.on.attr="at.risk" target.is.non.zero.on.attr="at.risk" condition.on.source="true">
    <consider.event.type name="email"/>
  </observation>
</eventnet.configuration>
'''


def aggregate_audit(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Build actor-free temporal readiness statistics."""
    timestamps = Counter(event["timestamp"] for event in events)
    time_tail_head = Counter((event["timestamp"], event["tail"], event["head"]) for event in events)
    head_arities = Counter(len(event["head"]) for event in events)
    actors = {event["tail"] for event in events}
    actors.update(actor for event in events for actor in event["head"])
    months = Counter(event["timestamp"].strftime("%Y-%m") for event in events)
    return {
        "event_records": len(events),
        "actors": len(actors),
        "sender_actors": len({event["tail"] for event in events}),
        "time_span_utc": {
            "minimum": min(event["timestamp"] for event in events).isoformat(),
            "maximum": max(event["timestamp"] for event in events).isoformat(),
        },
        "calendar_months": len(months),
        "head_arity_counts": {str(arity): count for arity, count in sorted(head_arities.items())},
        "multi_receiver_events": sum(count for arity, count in head_arities.items() if arity > 1),
        "distinct_timestamps": len(timestamps),
        "timestamp_tie_groups": sum(count > 1 for count in timestamps.values()),
        "records_in_timestamp_ties": sum(count for count in timestamps.values() if count > 1),
        "maximum_timestamp_tie_size": max(timestamps.values()),
        "same_timestamp_sender_head_groups": sum(count > 1 for count in time_tail_head.values()),
        "records_in_same_timestamp_sender_head_groups": sum(
            count for count in time_tail_head.values() if count > 1
        ),
        "maximum_same_timestamp_sender_head_group_size": max(time_tail_head.values()),
        "monthly_event_counts": {month: months[month] for month in sorted(months)},
    }


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Create a fresh protected local output directory."""
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: output directory is nonempty: {path}; pass --overwrite.")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_bundle(
    output_dir: Path,
    events: list[dict[str, Any]],
    *,
    tie_order: str,
    controls_per_event: int,
    halflife_seconds: int,
    eventnet_random_seed: int,
    input_path: Path,
    selection: dict[str, Any],
    folds: list[dict[str, Any]],
) -> dict[str, Any]:
    """Write the private Eventnet CSV, numeric map, configuration, and manifest."""
    actors = sorted(
        {event["tail"] for event in events}.union(*[set(event["head"]) for event in events])
    )
    actor_to_numeric = {actor: index for index, actor in enumerate(actors, start=1)}
    first_time = events[0]["timestamp"]

    with (output_dir / ACTOR_MAP_FILE).open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["actor_numeric_id", "custodian_id"])
        writer.writeheader()
        writer.writerows(
            {"actor_numeric_id": numeric, "custodian_id": actor}
            for actor, numeric in actor_to_numeric.items()
        )

    event_file = output_dir / EVENTNET_FILE
    with event_file.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["event_interval_id", "sender", "receiver", "time", "type", "weight"],
            lineterminator="\n",
        )
        writer.writeheader()
        for numeric in range(1, len(actors) + 1):
            writer.writerow(
                {
                    "event_interval_id": 0,
                    "sender": numeric,
                    "receiver": numeric,
                    "time": -1,
                    "type": "add.actor",
                    "weight": 1,
                }
            )
        for ordinal, event in enumerate(events, start=1):
            offset_seconds = int((event["timestamp"] - first_time).total_seconds())
            for receiver in event["head"]:
                writer.writerow(
                    {
                        "event_interval_id": ordinal,
                        "sender": actor_to_numeric[event["tail"]],
                        "receiver": actor_to_numeric[receiver],
                        "time": offset_seconds,
                        "type": "email",
                        "weight": 1,
                    }
                )

    with (output_dir / EVENT_INDEX_FILE).open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "event_interval_id",
                "event_id",
                "time_offset_seconds",
                "timestamp_utc",
                "month",
                "head_size",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for ordinal, event in enumerate(events, start=1):
            writer.writerow(
                {
                    "event_interval_id": ordinal,
                    "event_id": event["event_id"],
                    "time_offset_seconds": int((event["timestamp"] - first_time).total_seconds()),
                    "timestamp_utc": event["timestamp"].isoformat(),
                    "month": event["timestamp"].strftime("%Y-%m"),
                    "head_size": len(event["head"]),
                }
            )

    with (output_dir / ROLLING_FOLDS_FILE).open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "fold",
                "train_end_utc_exclusive",
                "test_start_utc_inclusive",
                "test_end_utc_exclusive",
                "training_events",
                "test_events",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(folds)

    (output_dir / EVENTNET_CONFIG).write_text(
        eventnet_config(controls_per_event, halflife_seconds, eventnet_random_seed),
        encoding="utf-8",
    )
    manifest = {
        "purpose": "directed_rhem_case_control_input_preparation",
        "source": {
            "native_event_path": recorded(input_path),
            "native_event_sha256": sha256_file(input_path),
        },
        "event_semantics": {
            "source": "singleton sender",
            "target": "nonempty unordered recipient set",
            "source_records_preserved": not selection[
                "same_timestamp_identical_footprints_collapsed"
            ],
            "same_timestamp_identical_footprint_sensitivity": selection[
                "same_timestamp_identical_footprints_collapsed"
            ],
            "paper1_projection_modified": False,
        },
        "actor_universe": selection,
        "time": {
            "utc": True,
            "eventnet_time_origin_utc": first_time.isoformat(),
            "eventnet_time_unit": "seconds",
            "event_interval_type": "EVENT_INTERVAL",
            "tie_order": tie_order,
            "tie_order_interpretation": (
                "A deterministic within-timestamp order used only for Eventnet interval processing; "
                "compare ascending and descending variants before interpreting history effects."
            ),
        },
        "risk_set": {
            "observation_type": "COND_SIZE_DHE_OBS",
            "controls_per_observed_event": controls_per_event,
            "eventnet_random_seed": eventnet_random_seed,
            "condition_on_target_size": True,
            "observations": {
                "FULL_EVENT": "sender plus receiver-set choice conditional on target size",
                "CONDITIONAL_SENDER_SET": "receiver-set choice conditional on sender and target size",
            },
        },
        "history": {
            "decay_half_life_seconds": halflife_seconds,
            "statistics": [
                "exact_rep",
                "dyad_rep",
                "reciprocation",
                "target_pair_rep",
                "receiver_interaction",
                "transitive_closure",
            ],
        },
        "counts": {
            "events": len(events),
            "actors": len(actors),
            "eventnet_incidence_rows": sum(len(event["head"]) for event in events),
        },
        "outputs": {
            "eventnet_csv": EVENTNET_FILE,
            "eventnet_config": EVENTNET_CONFIG,
            "actor_map_private": ACTOR_MAP_FILE,
            "event_index_private": EVENT_INDEX_FILE,
            "rolling_folds_private": ROLLING_FOLDS_FILE,
        },
    }
    (output_dir / MANIFEST_FILE).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def render_report(audit: dict[str, Any], manifest: dict[str, Any]) -> str:
    """Render an actor-free Markdown data-readiness audit."""
    arities = "\n".join(
        f"| {arity} | {count:,} |" for arity, count in audit["head_arity_counts"].items()
    )
    months = "\n".join(
        f"| {month} | {count:,} |" for month, count in audit["monthly_event_counts"].items()
    )
    return f"""# Enron temporal directed-hyperevent readiness audit

## Scope

This audit describes the existing Enron custodian native-event projection as an
input for a separate temporal directed-group-event study. It does not alter the
Paper 1 static projection, deduplicate source records, fit an RHEM, or make a
forecasting claim.

The event unit is one recorded email with one sender and a nonempty unordered
set of To-plus-Cc recipients. The actor policy and source date filter are the
already documented custodian projection policy.

- Event records: `{audit["event_records"]:,}`
- Actors: `{audit["actors"]:,}`
- Sender actors: `{audit["sender_actors"]:,}`
- UTC span: `{audit["time_span_utc"]["minimum"]}` to `{audit["time_span_utc"]["maximum"]}`
- Months with one or more events: `{audit["calendar_months"]:,}`
- Events with two or more recipients: `{audit["multi_receiver_events"]:,}`

## Origin-safe actor universe and forecast folds

The primary temporal pilot freezes `{manifest["actor_universe"]["core_size"]}`
actors by total sender-or-receiver participation strictly before
`{manifest["actor_universe"]["selection_origin_utc"]}`. Lexical actor identity
is only a deterministic tie-break. An event is retained only when its sender
and every receiver belong to this pre-origin universe. The retained sequence
contains `{manifest["actor_universe"]["pre_origin_retained_events"]:,}`
pre-origin events and `{manifest["actor_universe"]["retained_events_before_evaluation_end"]:,}`
events before the exclusive evaluation endpoint
`{manifest["actor_universe"]["evaluation_end_utc_exclusive"]}`. This prevents
the actor-selection rule from ranking the evaluation universe with future
participation.

The private bundle contains four predeclared expanding 2001 quarterly folds.
Each test event may use the history of earlier observed events, but model
coefficients must be estimated only from records preceding that fold's origin.

## Receiver-set sizes

| Recipients | Events |
|---:|---:|
{arities}

## Simultaneous-event sensitivity

The archive retains distinct source records under the existing message-copy
policy. `{audit["records_in_timestamp_ties"]:,}` records occur in timestamp
ties across `{audit["timestamp_tie_groups"]:,}` distinct timestamps; the
largest tie contains `{audit["maximum_timestamp_tie_size"]:,}` records.
`{audit["records_in_same_timestamp_sender_head_groups"]:,}` records occur in
groups sharing a timestamp, sender, and target set. These quantities do not
establish that such records are copies or duplicates; they show why a temporal
history model must expose its treatment of tied event times.

The Eventnet preparation records a deterministic interval order
`{manifest["time"]["tie_order"]}`. That order is not given a substantive
interpretation. The companion descending/ascending bundle is a required
sensitivity analysis before interpreting history-dependent effects.

## Candidate-event contract

The generated Eventnet configuration uses `COND_SIZE_DHE_OBS` with
`{manifest["risk_set"]["controls_per_observed_event"]}` sampled controls per
observed event. It conditions on recipient-set size. One observation is a full
sender-plus-recipient-set choice; the second additionally conditions on the
observed sender. The RHEM literature motivates sampled risk sets because the
full set of receiver subsets is exponential in the number of actors.

The history covariates have a `{manifest["history"]["decay_half_life_seconds"]:,}`
second decay half-life. They include whole-event repetition, directed dyad
repetition, directed reciprocation, receiver-pair repetition, receiver
interaction, and directed transitive closure. A later fitted analysis must
report the Eventnet version, random-sampling behavior, selected observation,
rolling-origin training boundary, and tied-time sensitivity.

## Monthly distribution

| Month | Events |
|:---|---:|
{months}

## Boundary

This is a data and risk-set readiness record. It is not a fitted RHEM,
TERGM, STERGM, or out-of-sample forecast result.
"""


def main() -> None:
    """Create a protected RHEM input bundle and safe aggregate readiness audit."""
    args = parse_args()
    input_path = resolve(args.input)
    output_dir = resolve(args.output_dir)
    audit_json = resolve(args.audit_json)
    audit_report = resolve(args.audit_report)
    selection_origin = parse_utc(args.core_selection_origin, option="--core-selection-origin")
    evaluation_end = parse_utc(args.evaluation_end, option="--evaluation-end")
    source_events = read_events(input_path)
    selected_events, selection = select_origin_safe_core(
        source_events,
        core_size=args.core_size,
        selection_origin=selection_origin,
        evaluation_end=evaluation_end,
    )
    removed_footprints = 0
    if args.collapse_same_timestamp_footprints:
        selected_events, removed_footprints = collapse_same_timestamp_footprints(selected_events)
    selection["same_timestamp_identical_footprints_collapsed"] = (
        args.collapse_same_timestamp_footprints
    )
    selection["same_timestamp_identical_records_removed"] = removed_footprints
    selection["events_after_optional_footprint_collapse"] = len(selected_events)
    ordered = order_events(selected_events, args.tie_order)
    folds = rolling_folds(ordered, selection_origin)
    audit = aggregate_audit(ordered)
    source_audit = aggregate_audit(source_events)

    existing = [path for path in (audit_json, audit_report) if path.exists()]
    if existing and not args.overwrite:
        rendered = ", ".join(recorded(path) for path in existing)
        raise SystemExit(f"STOP: aggregate audit output exists ({rendered}); pass --overwrite.")
    prepare_output_dir(output_dir, args.overwrite)
    manifest = write_bundle(
        output_dir,
        ordered,
        tie_order=args.tie_order,
        controls_per_event=args.controls_per_event,
        halflife_seconds=args.halflife_seconds,
        eventnet_random_seed=args.eventnet_random_seed,
        input_path=input_path,
        selection=selection,
        folds=folds,
    )
    audit_payload = {
        "dataset_id": "enron_20150507",
        "driver": "scripts/78_prepare_enron_rhem_inputs.py",
        "status": "temporal_directed_hyperevent_input_ready_not_fit",
        "source": {
            "native_event_path": recorded(input_path),
            "native_event_sha256": sha256_file(input_path),
        },
        "source_audit_before_actor_selection": source_audit,
        "selected_actor_universe": {
            key: value for key, value in selection.items() if key != "actor_ids_private"
        },
        "selected_event_audit": audit,
        "rolling_folds": folds,
        "eventnet_contract": {
            "time_order": args.tie_order,
            "controls_per_event": args.controls_per_event,
            "eventnet_random_seed": args.eventnet_random_seed,
            "halflife_seconds": args.halflife_seconds,
            "event_interval_semantics": manifest["time"]["event_interval_type"],
            "observations": manifest["risk_set"]["observations"],
        },
        "limitations": [
            "The source record policy is preserved; same-timestamp records are not assumed to be duplicates.",
            "Within-timestamp Eventnet ordering is a sensitivity condition, not a substantive order claim.",
            "The output is an Eventnet input and candidate-generation contract, not a fitted RHEM or forecast result.",
        ],
    }
    audit_json.parent.mkdir(parents=True, exist_ok=True)
    audit_report.parent.mkdir(parents=True, exist_ok=True)
    audit_json.write_text(
        json.dumps(audit_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    audit_report.write_text(render_report(audit, manifest), encoding="utf-8")

    print("Enron directed-RHEM input preparation complete.")
    print(f"Events: {len(ordered):,}; actors: {audit['actors']:,}")
    print(f"Tie order: {args.tie_order}; controls per event: {args.controls_per_event:,}")
    print(f"Private Eventnet bundle: {recorded(output_dir)}")
    print(f"Aggregate audit: {recorded(audit_json)}")


if __name__ == "__main__":
    main()
