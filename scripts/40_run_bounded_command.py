#!/usr/bin/env python3
"""Run a local command with a wall-clock limit and an auditable log."""

from __future__ import annotations

import argparse
import os
import shlex
import signal
import subprocess
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a command with a hard wall-clock limit and write combined output to a log."
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        required=True,
        help="Positive wall-clock limit in seconds.",
    )
    parser.add_argument(
        "--log",
        type=Path,
        required=True,
        help="Path for the combined command output and runner status.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command after --, for example: -- Rscript model.R --option=value",
    )
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive.")
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("Provide a command after --.")
    return args


def terminate_process_group(process: subprocess.Popen[object]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        process.wait(timeout=5)


def main() -> int:
    args = parse_args()
    args.log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    command_text = shlex.join(args.command)

    with args.log.open("w", encoding="utf-8", buffering=1) as log:
        log.write("Bounded command runner\n")
        log.write(f"Timeout seconds: {args.timeout_seconds:g}\n")
        log.write(f"Command: {command_text}\n")
        log.write("\n===== COMMAND OUTPUT =====\n")
        log.flush()
        process = subprocess.Popen(
            args.command,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )
        timed_out = False
        try:
            return_code = process.wait(timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate_process_group(process)
            return_code = process.returncode
        elapsed = time.monotonic() - started
        log.write("\n===== RUNNER STATUS =====\n")
        log.write(f"Elapsed seconds: {elapsed:.3f}\n")
        if timed_out:
            log.write(f"Status: timed_out_after_{args.timeout_seconds:g}_seconds\n")
            log.write(f"Process return code after termination: {return_code}\n")
        else:
            log.write(f"Status: completed\nProcess return code: {return_code}\n")

    if timed_out:
        print(
            f"Timed out after {args.timeout_seconds:g} seconds. "
            f"The process group was terminated. Log: {args.log}"
        )
        return 124
    print(f"Completed with exit code {return_code}. Log: {args.log}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
