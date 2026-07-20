"""Tests for HTML report generation."""

from pathlib import Path

from pdie.engine import Engine
from pdie.reports.html_report import HtmlReport


def test_analyze_generates_html_report(sample_workbook: Path) -> None:
    """Analyze writes a report next to the source workbook."""
    output_path = sample_workbook.with_suffix(".html")
    if output_path.exists():
        output_path.unlink()

    workbook = Engine().analyze(sample_workbook)

    assert output_path.exists()
    report = output_path.read_text(encoding="utf-8")
    assert f"{workbook.name} Workbook Analysis" in report
    assert "Workbook Overview" in report
    assert "Cell Metadata" in report
    assert "editable" in report
    assert "protected" in report
    assert "formula" in report
    assert "dropdown" in report
    assert "merged" in report
    assert "hidden" in report


def test_html_report_uses_explicit_output_path(sample_workbook: Path, tmp_path: Path) -> None:
    """Report generation supports caller-provided output paths."""
    workbook = Engine().analyze(sample_workbook)
    report_path = tmp_path / "review.html"

    generated_path = HtmlReport().generate(workbook, report_path)

    assert generated_path == report_path
    assert report_path.exists()
    assert "Click a cell to inspect metadata" in report_path.read_text(encoding="utf-8")
