#!/usr/bin/env python3
"""Acquire a versioned public Bioguide-keyed historical legislator roster.

The GPO Bill Status source supplies event records but not a person-tenure roster.
This driver snapshots the documented ``congress-legislators`` current and historical
JSON files, which together expose Bioguide IDs and Senate term dates. The roster is
used only to define and audit fixed actor-universe policies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = "https://raw.githubusercontent.com/unitedstates/congress-legislators/gh-pages"
USER_AGENT = "directed-hp-lp-ergms-research/0.1 (reproducible public-data acquisition)"
FILES = ("legislators-current.json", "legislators-historical.json")


def parse_args() -> argparse.Namespace:
    """Parse explicit output paths and bounded retry controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-dir", type=Path, default=Path("data/raw/us_congress_legislators_gh_pages")
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=Path("data/metadata/us_congress_legislators_gh_pages_acquisition.json"),
    )
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.retries <= 10:
        parser.error("--retries must be between 1 and 10.")
    if args.timeout_seconds < 10:
        parser.error("--timeout-seconds must be at least 10.")
    return args


def resolve(path: Path) -> Path:
    """Resolve project-relative file paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Render a repository-relative provenance path when possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256(payload: bytes) -> str:
    """Return the stable content hash of a downloaded roster snapshot."""
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str, timeout_seconds: int, retries: int) -> bytes:
    """Fetch a public source file with bounded retries."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    errors: list[str] = []
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                payload = response.read()
            if not payload:
                raise RuntimeError("empty response")
            return payload
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError) as error:
            errors.append(f"attempt {attempt + 1}: {error}")
            if attempt + 1 < retries:
                time.sleep(min(12.0, 0.75 * (2**attempt)))
    raise RuntimeError(f"could not fetch {url}: {'; '.join(errors)}")


def validate_roster(payload: bytes, filename: str) -> int:
    """Verify documented roster JSON structure before storing a raw snapshot."""
    try:
        values = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError(f"{filename} is not valid JSON") from error
    if not isinstance(values, list) or not values:
        raise ValueError(f"{filename} must contain a nonempty record list")
    if not all(isinstance(value, dict) and isinstance(value.get("id"), dict) for value in values):
        raise ValueError(f"{filename} does not contain legislator ID records")
    return len(values)


def main() -> None:
    """Snapshot current and historical roster files with compact provenance metadata."""
    args = parse_args()
    raw_dir, metadata_path = resolve(args.raw_dir), resolve(args.metadata_output)
    raw_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for filename in FILES:
        output = raw_dir / filename
        source_url = f"{SOURCE_ROOT}/{filename}"
        if output.is_file() and not args.refresh:
            payload = output.read_bytes()
            disposition = "reused"
        else:
            payload = fetch(source_url, args.timeout_seconds, args.retries)
            temporary = output.with_suffix(".json.part")
            temporary.write_bytes(payload)
            temporary.replace(output)
            disposition = "downloaded"
        records.append(
            {
                "filename": filename,
                "source_url": source_url,
                "sha256": sha256(payload),
                "bytes": len(payload),
                "records": validate_roster(payload, filename),
                "disposition": disposition,
            }
        )
    metadata = {
        "dataset_id": "us_congress_legislators_gh_pages",
        "status": "acquired",
        "source": {
            "provider": "unitedstates/congress-legislators",
            "branch": "gh-pages",
            "documentation_url": "https://github.com/unitedstates/congress-legislators",
            "accessed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "raw_tree": {"path": recorded(raw_dir), "files": records},
        "run": {
            "driver": "scripts/64_acquire_congress_legislator_roster.py",
            "retries": args.retries,
        },
        "scope": (
            "Public Bioguide-keyed member and term records used only to define Senate actor "
            "universe policies; Bill Status XML remains the event-record source."
        ),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Historical legislator roster acquisition passed.")
    print(f"Files: {len(records):,}; records: {sum(int(row['records']) for row in records):,}.")
    print(f"Metadata: {recorded(metadata_path)}")


if __name__ == "__main__":
    main()
