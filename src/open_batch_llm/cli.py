"""CLI entry point for open-batch-llm."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """open-batch-llm: Manage and run batch LLM calls."""


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--provider",
    default="openai",
    show_default=True,
    help="LLM provider to use (e.g. openai, anthropic).",
)
@click.option(
    "--model",
    default="gpt-4o-mini",
    show_default=True,
    help="Model name to use for completions.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (JSON). Defaults to stdout.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Validate the input file without making any API calls.",
)
def run(
    input_file: Path,
    provider: str,
    model: str,
    output: Path | None,
    dry_run: bool,
) -> None:
    """Run batch LLM calls from INPUT_FILE.

    INPUT_FILE must be a JSON file containing a list of request objects.
    Each object should have a \"prompt\" key with the text to send.

    \b
    Example INPUT_FILE:
        [
          {"id": "req-1", "prompt": "What is 2 + 2?"},
          {"id": "req-2", "prompt": "Name the planets of the solar system."}
        ]
    """
    try:
        requests = json.loads(input_file.read_text())
    except json.JSONDecodeError as exc:
        console.print(f"[red]Error:[/red] Invalid JSON in {input_file}: {exc}")
        sys.exit(1)

    if not isinstance(requests, list):
        console.print("[red]Error:[/red] Input file must contain a JSON array of request objects.")
        sys.exit(1)

    console.print(
        f"[green]Loaded[/green] {len(requests)} request(s) from [bold]{input_file}[/bold]"
    )
    console.print(f"Provider: [cyan]{provider}[/cyan]  Model: [cyan]{model}[/cyan]")

    if dry_run:
        console.print("[yellow]Dry-run mode — no API calls will be made.[/yellow]")
        _print_requests_table(requests)
        return

    console.print(
        "[dim]Note: API calls are not yet implemented. "
        "Use --dry-run to inspect the request list.[/dim]"
    )
    _print_requests_table(requests)

    results = [
        {"id": req.get("id", i), "prompt": req.get("prompt", ""), "response": None}
        for i, req in enumerate(requests)
    ]

    if output:
        output.write_text(json.dumps(results, indent=2))
        console.print(f"[green]Results written to[/green] {output}")
    else:
        click.echo(json.dumps(results, indent=2))


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path) -> None:
    """Validate the structure of INPUT_FILE without making any API calls."""
    try:
        requests = json.loads(input_file.read_text())
    except json.JSONDecodeError as exc:
        console.print(f"[red]Error:[/red] Invalid JSON in {input_file}: {exc}")
        sys.exit(1)

    if not isinstance(requests, list):
        console.print("[red]Error:[/red] Input file must contain a JSON array.")
        sys.exit(1)

    issues: list[str] = []
    for i, req in enumerate(requests):
        if not isinstance(req, dict):
            issues.append(f"Item {i} is not an object.")
        elif "prompt" not in req:
            issues.append(f"Item {i} is missing required key 'prompt'.")

    if issues:
        console.print("[red]Validation failed:[/red]")
        for issue in issues:
            console.print(f"  • {issue}")
        sys.exit(1)

    console.print(
        f"[green]✓ Valid[/green] — {len(requests)} request(s) in [bold]{input_file}[/bold]"
    )


def _print_requests_table(requests: list) -> None:
    table = Table(title="Batch Requests", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("ID")
    table.add_column("Prompt")

    for i, req in enumerate(requests):
        prompt = str(req.get("prompt", ""))
        if len(prompt) > 80:
            prompt = prompt[:77] + "..."
        table.add_row(str(i), str(req.get("id", i)), prompt)

    console.print(table)
