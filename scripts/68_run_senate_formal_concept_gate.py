#!/usr/bin/env python3
"""Run cap-first formal-concept feasibility audits for the prepared Senate graph.

Each requested head cap is evaluated independently with the existing bounded
formal-concept driver. Failures to enumerate within the declared candidate
budget are recorded as feasibility-gate outcomes rather than hidden or retried
with a different specification.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMAL_CONCEPT_DRIVER = PROJECT_ROOT / "scripts" / "28_audit_formal_concepts.py"


def parse_args() -> argparse.Namespace:
    """Parse the fixed-graph, cap-grid formal-concept feasibility contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", default="senate_118_s_bills")
    parser.add_argument(
        "--edges",
        type=Path,
        default=Path("data/processed/senate_118_s_bills/static_arcs.parquet"),
    )
    parser.add_argument(
        "--nodes", type=Path, default=Path("data/processed/senate_118_s_bills/nodes.csv")
    )
    parser.add_argument("--node-column", default="node")
    parser.add_argument("--tail-cap", type=int, default=3)
    parser.add_argument("--head-caps", default="1,2,3,5,10")
    parser.add_argument("--max-candidates", type=int, default=250_000)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("results/phase2/senate_118_s_bills_cap_gate")
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        head_caps = tuple(
            sorted({int(item.strip()) for item in args.head_caps.split(",") if item.strip()})
        )
    except ValueError as error:
        parser.error(f"--head-caps must be comma-separated positive integers: {error}")
    if (
        args.tail_cap < 1
        or args.max_candidates < 1
        or not head_caps
        or any(cap < 1 for cap in head_caps)
    ):
        parser.error("all caps and --max-candidates must be positive.")
    args.head_caps = head_caps
    return args


def resolve(path: Path) -> Path:
    """Resolve a project-relative source or output path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Render a repository-relative path when it lies in this project."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty stable CSV table."""
    if not rows:
        raise RuntimeError(f"cannot write empty concept-feasibility table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def owned_files(output_dir: Path) -> tuple[Path, ...]:
    """List only summary files owned directly by this cap-gate wrapper."""
    return tuple(
        output_dir / name
        for name in ("formal_concept_feasibility.csv", "summary.json", "summary.md")
    )


def prepare_output(output_dir: Path, overwrite: bool) -> None:
    """Prevent accidental replacement of cap-specific concept audit bundles."""
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path for path in owned_files(output_dir) if path.exists()]
    if existing and not overwrite:
        raise SystemExit(
            "STOP: concept-feasibility summary exists; pass --overwrite to refresh the wrapper "
            "summary and each requested cap-specific audit."
        )
    for path in existing:
        path.unlink()


def output_for(output_dir: Path, tail_cap: int, head_cap: int) -> Path:
    """Return a deterministic output directory owned by one cap combination."""
    return output_dir / f"formal_concepts_tail{tail_cap}_head{head_cap}"


def run_one(
    args: argparse.Namespace,
    edges: Path,
    nodes: Path,
    output_dir: Path,
    head_cap: int,
) -> dict[str, object]:
    """Run one cap-first concept audit and record success or an explicit feasibility failure."""
    destination = output_for(output_dir, args.tail_cap, head_cap)
    if destination.exists() and args.overwrite:
        shutil.rmtree(destination)
    command = [
        sys.executable,
        str(FORMAL_CONCEPT_DRIVER),
        "--dataset",
        args.dataset_id,
        "--edges",
        str(edges),
        "--nodes",
        str(nodes),
        "--source-col",
        "tail",
        "--target-col",
        "head",
        "--node-col",
        args.node_column,
        "--tail-cap",
        str(args.tail_cap),
        "--head-cap",
        str(head_cap),
        "--max-candidates",
        str(args.max_candidates),
        "--output-dir",
        str(destination),
    ]
    started = time.monotonic()
    completed = subprocess.run(
        command, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
    )
    elapsed = time.monotonic() - started
    base = {
        "tail_cap": args.tail_cap,
        "head_cap": head_cap,
        "max_candidates": args.max_candidates,
        "elapsed_seconds": elapsed,
        "output_dir": recorded(destination),
        "footprint_coverage": "",
    }
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip().replace("\n", " ")
        return {**base, "status": "feasibility_gate_failed", "concepts": "", "message": message}
    summary_path = destination / "summary.json"
    if not summary_path.is_file():
        return {
            **base,
            "status": "feasibility_gate_failed",
            "concepts": "",
            "message": "formal-concept driver returned success but emitted no summary.json",
        }
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    concepts = summary.get("concepts", {}).get("count")
    if not isinstance(concepts, int):
        return {
            **base,
            "status": "feasibility_gate_failed",
            "concepts": "",
            "message": "formal-concept summary lacks integer concept count",
        }
    return {
        **base,
        "status": "completed",
        "concepts": concepts,
        "footprint_coverage": summary["concepts"]["capped_footprint_arc_coverage"],
        "message": "",
    }


def main() -> None:
    """Evaluate each requested cap without silently changing the concept search budget."""
    args = parse_args()
    edges, nodes, output_dir = resolve(args.edges), resolve(args.nodes), resolve(args.output_dir)
    if not edges.is_file() or not nodes.is_file():
        raise SystemExit(
            "STOP: prepared Senate static arcs and node table must exist before concept gate."
        )
    prepare_output(output_dir, args.overwrite)
    rows = [run_one(args, edges, nodes, output_dir, head_cap) for head_cap in args.head_caps]
    write_csv(output_dir / "formal_concept_feasibility.csv", rows)
    manifest = {
        "driver": "scripts/68_run_senate_formal_concept_gate.py",
        "dataset_id": args.dataset_id,
        "inputs": {"edges": recorded(edges), "nodes": recorded(nodes)},
        "tail_cap": args.tail_cap,
        "head_caps": list(args.head_caps),
        "max_candidates": args.max_candidates,
        "outcomes": rows,
        "interpretation": (
            "A feasibility-gate failure means cap-first enumeration did not complete under the "
            "declared candidate budget. It is not a substitute for a different cap or algorithm."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Senate cap-first formal-concept feasibility gate",
        "",
        f"- Dataset: `{args.dataset_id}`",
        f"- Formal tail cap: `{args.tail_cap}`",
        f"- Candidate budget per cap: `{args.max_candidates:,}`",
        "",
        "| Tail cap | Head cap | Status | Concepts | Footprint coverage | Seconds |",
        "|---:|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        concepts = row["concepts"] if row["concepts"] != "" else "--"
        coverage = row.get("footprint_coverage")
        coverage_text = f"{float(coverage):.3%}" if isinstance(coverage, (float, int)) else "--"
        lines.append(
            "| {tail_cap} | {head_cap} | {status} | {concepts} | {coverage} | "
            "{elapsed_seconds:.2f} |".format(
                tail_cap=row["tail_cap"],
                head_cap=row["head_cap"],
                status=row["status"],
                concepts=concepts,
                coverage=coverage_text,
                elapsed_seconds=float(row["elapsed_seconds"]),
            )
        )
    lines.extend(
        [
            "",
            "A failed row is retained as a cap-feasibility outcome. The detailed cap-specific "
            "directories contain completed concept lists only for successful rows.",
            "",
        ]
    )
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    completed = sum(row["status"] == "completed" for row in rows)
    print("Senate formal-concept feasibility gate complete.")
    print(f"Completed caps: {completed:,}/{len(rows):,}.")
    print(f"Output bundle: {recorded(output_dir)}")


if __name__ == "__main__":
    main()
