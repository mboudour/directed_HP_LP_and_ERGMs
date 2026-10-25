#!/usr/bin/env python3
"""Acquire an official GPO Bill Status measure directory reproducibly.

The driver downloads only XML records advertised by the official GovInfo listing,
resumes safely, records checksums, and emits a compact tracked acquisition record.
Raw XML and the detailed per-file manifest remain outside Git under ``data/raw``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOVINFO_ROOT = "https://www.govinfo.gov"
USER_AGENT = "directed-hp-lp-ergms-research/0.1 (reproducible public-data acquisition)"


@dataclass(frozen=True, slots=True)
class DownloadRecord:
    """One raw XML file and its verified byte-level identity."""

    filename: str
    source_url: str
    sha256: str
    bytes: int
    disposition: str


def parse_args() -> argparse.Namespace:
    """Parse an explicit public-source acquisition contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--congress", type=int, default=118)
    parser.add_argument("--measure-prefix", default="s")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw/us_senate_118_billstatus_s"),
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=Path("data/metadata/us_senate_118_billstatus_s_acquisition.json"),
    )
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.congress < 1:
        parser.error("--congress must be positive.")
    if not re.fullmatch(r"[a-z]+", args.measure_prefix):
        parser.error("--measure-prefix must contain lowercase letters only.")
    if args.workers < 1 or args.workers > 32:
        parser.error("--workers must be between 1 and 32.")
    if args.retries < 1 or args.retries > 10:
        parser.error("--retries must be between 1 and 10.")
    if args.timeout_seconds < 10:
        parser.error("--timeout-seconds must be at least 10.")
    return args


def resolve_path(path: Path) -> Path:
    """Resolve repository-relative input and output paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Render a repository-relative provenance path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256_bytes(payload: bytes) -> str:
    """Return the SHA-256 digest of an in-memory public listing."""
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    """Calculate a streaming SHA-256 checksum for a raw XML file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_bytes(
    url: str,
    timeout_seconds: int,
    retries: int,
    *,
    accept: str | None = None,
) -> bytes:
    """Fetch a public URL with bounded retry handling for transient failures."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    request = urllib.request.Request(url, headers=headers)
    failures: list[str] = []
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                payload = response.read()
            if not payload:
                raise RuntimeError("empty response")
            return payload
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError) as error:
            failures.append(f"attempt {attempt + 1}: {error}")
            if attempt + 1 < retries:
                time.sleep(min(12.0, 0.75 * (2**attempt)))
    raise RuntimeError(f"could not fetch {url}: {'; '.join(failures)}")


def listing_url(congress: int, measure_prefix: str) -> str:
    """Return the official directory listing URL for one Congress and measure class."""
    return f"{GOVINFO_ROOT}/bulkdata/json/BILLSTATUS/{congress}/{measure_prefix}"


def parse_listing(payload: bytes, congress: int, measure_prefix: str) -> tuple[str, ...]:
    """Validate and return XML download paths from the official JSON directory index."""
    try:
        listing = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError("GovInfo listing is not valid JSON") from error
    if not isinstance(listing, dict) or not isinstance(listing.get("files"), list):
        raise ValueError("GovInfo JSON directory index lacks a files list")
    pattern = re.compile(
        rf"^/bulkdata/BILLSTATUS/{congress}/{re.escape(measure_prefix)}/"
        rf"BILLSTATUS-{congress}{re.escape(measure_prefix)}[1-9][0-9]*\.xml$"
    )
    paths: set[str] = set()
    for entry in listing["files"]:
        if not isinstance(entry, dict):
            continue
        link = entry.get("link")
        if not isinstance(link, str):
            continue
        parsed = urllib.parse.urlparse(link)
        if parsed.scheme != "https" or parsed.netloc != "www.govinfo.gov":
            continue
        if pattern.fullmatch(parsed.path):
            paths.add(parsed.path)
    paths = sorted(paths)
    if not paths:
        raise ValueError("official listing contained no matching bill-status XML files")
    expected_names = [Path(path).name for path in paths]
    if len(set(expected_names)) != len(expected_names):
        raise ValueError("official listing contains duplicate XML filenames")
    return tuple(paths)


def validate_xml_payload(payload: bytes, url: str) -> None:
    """Reject HTML error pages or empty files before adding raw source data."""
    prefix = payload.lstrip()[:128].lower()
    if not prefix.startswith(b"<?xml") and not prefix.startswith(b"<billstatus"):
        raise ValueError(f"response is not Bill Status XML: {url}")


def fetch_one(
    relative_path: str,
    raw_dir: Path,
    timeout_seconds: int,
    retries: int,
    refresh: bool,
) -> DownloadRecord:
    """Acquire one source XML atomically or verify a resumable prior acquisition."""
    filename = Path(relative_path).name
    source_url = urllib.parse.urljoin(GOVINFO_ROOT, relative_path)
    destination = raw_dir / filename
    if destination.is_file() and not refresh:
        return DownloadRecord(
            filename=filename,
            source_url=source_url,
            sha256=sha256_file(destination),
            bytes=destination.stat().st_size,
            disposition="reused",
        )
    payload = fetch_bytes(source_url, timeout_seconds, retries)
    validate_xml_payload(payload, source_url)
    temporary = destination.with_suffix(".xml.part")
    temporary.write_bytes(payload)
    temporary.replace(destination)
    return DownloadRecord(
        filename=filename,
        source_url=source_url,
        sha256=sha256_bytes(payload),
        bytes=len(payload),
        disposition="downloaded",
    )


def source_tree_sha256(records: tuple[DownloadRecord, ...]) -> str:
    """Hash ordered file names and checksums as a compact raw-tree identity."""
    digest = hashlib.sha256()
    for record in records:
        digest.update(record.filename.encode("utf-8"))
        digest.update(b"\0")
        digest.update(record.sha256.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    """Write deterministic JSON with a final newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    """Acquire, checksum, and register the declared official Bill Status directory."""
    args = parse_args()
    raw_dir = resolve_path(args.raw_dir)
    metadata_output = resolve_path(args.metadata_output)
    source_listing_url = listing_url(args.congress, args.measure_prefix)
    listing_payload = fetch_bytes(
        source_listing_url,
        args.timeout_seconds,
        args.retries,
        accept="application/json",
    )
    relative_paths = parse_listing(listing_payload, args.congress, args.measure_prefix)

    if raw_dir.exists() and not raw_dir.is_dir():
        raise SystemExit(f"STOP: raw output path is not a directory: {raw_dir}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    listing_cache = raw_dir / "SOURCE_LISTING.json"
    listing_cache.write_bytes(listing_payload)

    records: list[DownloadRecord] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                fetch_one,
                relative_path,
                raw_dir,
                args.timeout_seconds,
                args.retries,
                args.refresh,
            ): relative_path
            for relative_path in relative_paths
        }
        for index, future in enumerate(as_completed(futures), start=1):
            relative_path = futures[future]
            try:
                record = future.result()
            except Exception as error:  # noqa: BLE001
                raise SystemExit(f"STOP: failed source record {relative_path}: {error}") from error
            records.append(record)
            if index % 250 == 0 or index == len(futures):
                print(f"Acquired or verified {index:,}/{len(futures):,} official XML records.")

    records_tuple = tuple(sorted(records, key=lambda record: record.filename))
    detailed_manifest = {
        "source_listing_url": source_listing_url,
        "source_listing_sha256": sha256_bytes(listing_payload),
        "congress": args.congress,
        "measure_prefix": args.measure_prefix,
        "records": [asdict(record) for record in records_tuple],
        "source_tree_sha256": source_tree_sha256(records_tuple),
    }
    write_json(raw_dir / "SOURCE_MANIFEST.json", detailed_manifest)
    record_counts = {
        disposition: sum(record.disposition == disposition for record in records_tuple)
        for disposition in ("downloaded", "reused")
    }
    compact_metadata = {
        "dataset_id": f"us_senate_{args.congress}_billstatus_{args.measure_prefix}",
        "status": "acquired",
        "source": {
            "provider": "U.S. Government Publishing Office GovInfo",
            "listing_url": source_listing_url,
            "listing_sha256": sha256_bytes(listing_payload),
            "accessed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "scope": {
            "congress": args.congress,
            "measure_prefix": args.measure_prefix,
            "record_type": "BILLSTATUS XML",
        },
        "raw_tree": {
            "path": recorded_path(raw_dir),
            "xml_records": len(records_tuple),
            "total_xml_bytes": sum(record.bytes for record in records_tuple),
            "tree_sha256": source_tree_sha256(records_tuple),
            "detailed_manifest": str((raw_dir / "SOURCE_MANIFEST.json").relative_to(raw_dir)),
        },
        "run": {
            "driver": "scripts/63_acquire_senate_billstatus.py",
            "workers": args.workers,
            "retries": args.retries,
            "downloaded": record_counts["downloaded"],
            "reused": record_counts["reused"],
        },
        "privacy": "Official public legislative source; raw XML remains excluded from Git.",
    }
    write_json(metadata_output, compact_metadata)
    print("Official Senate Bill Status acquisition passed.")
    print(f"Dataset: {compact_metadata['dataset_id']}.")
    print(f"XML records: {len(records_tuple):,}.")
    print(f"Raw XML bytes: {compact_metadata['raw_tree']['total_xml_bytes']:,}.")
    print(f"Metadata: {recorded_path(metadata_output)}")


if __name__ == "__main__":
    main()
