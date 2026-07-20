"""CLI entry point for PDIE using Typer."""

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from pdie.engine import Engine

app = typer.Typer(
    help="PDIE - ProAssist Document Intelligence Engine",
    no_args_is_help=True,
)
console = Console()
engine = Engine()


@app.command()
def analyze(
    workbook_path: Annotated[Path, typer.Argument(help="Path to the workbook to analyze")],
) -> None:
    """Analyze a workbook and generate metadata and reports.

    Example:
        pdie analyze workbook.xlsm
    """
    try:
        workbook_path = Path(workbook_path).resolve()
        if not workbook_path.exists():
            console.print(
                f"[red]Error:[/red] File not found: {workbook_path}"
            )
            sys.exit(1)

        console.print(
            f"[cyan]Analyzing:[/cyan] {workbook_path.name}",
        )
        workbook = engine.analyze(workbook_path)

        table = Table(title="Workbook Analysis")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Workbook", workbook.name)
        table.add_row("Worksheets", str(workbook.worksheet_count()))
        table.add_row("Total Cells", str(workbook.total_cells()))
        table.add_row("Formulas", str(workbook.total_formulas()))
        table.add_row("Editable Cells", str(workbook.total_editable_cells()))

        console.print(table)
        console.print("[green]✓[/green] Analysis complete")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def compare(
    old_workbook: Annotated[Path, typer.Argument(help="Path to the original workbook")],
    new_workbook: Annotated[Path, typer.Argument(help="Path to the new workbook")],
) -> None:
    """Compare two workbook versions and detect changes.

    Example:
        pdie compare old.xlsm new.xlsm
    """
    try:
        old_path = Path(old_workbook).resolve()
        new_path = Path(new_workbook).resolve()

        if not old_path.exists():
            console.print(f"[red]Error:[/red] File not found: {old_path}")
            sys.exit(1)
        if not new_path.exists():
            console.print(f"[red]Error:[/red] File not found: {new_path}")
            sys.exit(1)

        console.print(
            f"[cyan]Comparing:[/cyan] {old_path.name} -> {new_path.name}"
        )
        result = engine.compare(old_path, new_path)

        console.print(f"[green]✓[/green] Comparison complete: {result}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def package(
    workbook_path: Annotated[Path, typer.Argument(help="Path to the workbook to package")],
) -> None:
    """Package a workbook as a Smart Template.

    Example:
        pdie package workbook.xlsm
    """
    try:
        workbook_path = Path(workbook_path).resolve()
        if not workbook_path.exists():
            console.print(
                f"[red]Error:[/red] File not found: {workbook_path}"
            )
            sys.exit(1)

        console.print(
            f"[cyan]Packaging:[/cyan] {workbook_path.name}",
        )
        result = engine.package(workbook_path)
        console.print(f"[green]✓[/green] Package created: {result}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def fill(
    template_path: Annotated[Path, typer.Argument(help="Path to the template file")],
    data_path: Annotated[Path, typer.Argument(help="Path to the JSON data file")],
) -> None:
    """Fill a Smart Template with data from a JSON file.

    Example:
        pdie fill template.template answers.json
    """
    try:
        template_path = Path(template_path).resolve()
        data_path = Path(data_path).resolve()

        if not template_path.exists():
            console.print(
                f"[red]Error:[/red] Template not found: {template_path}"
            )
            sys.exit(1)
        if not data_path.exists():
            console.print(
                f"[red]Error:[/red] Data file not found: {data_path}"
            )
            sys.exit(1)

        console.print(
            f"[cyan]Filling:[/cyan] {template_path.name} with {data_path.name}"
        )
        result = engine.fill(template_path, data_path)
        console.print(f"[green]✓[/green] Template filled: {result}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def validate(
    template_path: Annotated[Path, typer.Argument(help="Path to the template to validate")],
) -> None:
    """Validate a Smart Template.

    Example:
        pdie validate template.template
    """
    try:
        template_path = Path(template_path).resolve()
        if not template_path.exists():
            console.print(
                f"[red]Error:[/red] Template not found: {template_path}"
            )
            sys.exit(1)

        console.print(
            f"[cyan]Validating:[/cyan] {template_path.name}",
        )
        result = engine.validate(template_path)
        console.print(f"[green]✓[/green] Validation result: {result}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
