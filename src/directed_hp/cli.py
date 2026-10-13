"""Command-line entry points for the directed HP/LP/ERGM project."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.callback()
def main() -> None:
    """Utilities for the directed HP/LP/ERGM project."""


@app.command()
def paths() -> None:
    """Print the project-relative locations used by the pipeline."""
    root = Path(__file__).resolve().parents[2]
    typer.echo(f"project_root={root}")
    typer.echo(f"data_root={root / 'data'}")
    typer.echo(f"results_root={root / 'results'}")


if __name__ == "__main__":
    app()
