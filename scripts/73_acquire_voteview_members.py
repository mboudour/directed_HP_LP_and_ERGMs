#!/usr/bin/env python3
"""Acquire the public Voteview member-ideology table with a provenance manifest.

The live Voteview CSV is mutable. This driver records its URL, retrieval time,
SHA-256 digest, byte count, and header so downstream political-covariate
preparation can be reproduced from the downloaded snapshot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://voteview.com/static/data/out/members/HSall_members.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "voteview_members" / "HSall_members.csv"
DEFAULT_METADATA = PROJECT_ROOT / "data" / "metadata" / "voteview_members_acquisition.json"
CHUNK_SIZE = 1 << 20


def parse_args() -> argparse.Namespace:
    """Parse explicit output and overwrite controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve a project-relative output path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def relative(path: Path) -> str:
    """Render a repository-relative path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def acquire(url: str, output: Path, overwrite: bool) -> dict[str, object]:
    """Download one CSV atomically while calculating its checksum."""
    if output.exists() and not overwrite:
        raise SystemExit(f"STOP: output already exists; pass --overwrite: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".part")
    temporary.unlink(missing_ok=True)
    digest = hashlib.sha256()
    try:
        with requests.get(url, stream=True, timeout=(30, 180)) as response:
            response.raise_for_status()
            with temporary.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        handle.write(chunk)
                        digest.update(chunk)
    except requests.RequestException as error:
        temporary.unlink(missing_ok=True)
        raise SystemExit(f"STOP: Voteview download failed: {error}") from error
    if temporary.stat().st_size == 0:
        temporary.unlink(missing_ok=True)
        raise SystemExit("STOP: Voteview download is empty.")
    temporary.replace(output)
    header = output.open(encoding="utf-8").readline().rstrip("\n\r").split(",")
    return {
        "url": url,
        "sha256": digest.hexdigest(),
        "bytes": output.stat().st_size,
        "header": header,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
    }


def main() -> None:
    """Acquire the Voteview member table and write provenance metadata."""
    args = parse_args()
    output = resolve(args.output)
    metadata = resolve(args.metadata)
    payload = acquire(args.url, output, args.overwrite)
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(
        json.dumps(
            {
                "dataset": "voteview_members",
                "purpose": "118th Senate DW-NOMINATE first-dimension covariate source",
                "download": payload,
                "output": relative(output),
                "interpretation": (
                    "Voteview is a mutable public source; the retrieval timestamp and checksum "
                    "identify the exact source snapshot used downstream."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("Voteview member acquisition passed.")
    print(f"Bytes: {payload['bytes']:,}; SHA-256: {payload['sha256']}")
    print(f"Output: {relative(output)}")
    print(f"Metadata: {relative(metadata)}")


if __name__ == "__main__":
    main()
