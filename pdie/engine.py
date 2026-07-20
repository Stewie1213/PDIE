"""Main engine coordinator for PDIE."""

from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from pdie.analyzers.workbook_fingerprinter import WorkbookFingerprinter
from pdie.core.workbook import Workbook
from pdie.readers.excel_reader import ExcelReader
from pdie.reports.html_report import HtmlReport


class Engine:
    """Main coordinator for PDIE operations."""

    def __init__(self) -> None:
        """Initialize the engine."""
        self.reader = ExcelReader()
        self.fingerprinter = WorkbookFingerprinter()
        self.html_report = HtmlReport()

    def analyze(self, workbook_path: Path) -> Workbook:
        """Analyze a workbook and write an HTML review report."""
        workbook = self.reader.read(workbook_path)
        workbook.fingerprint = self.fingerprinter.fingerprint_workbook(workbook)
        openpyxl_wb = load_workbook(workbook_path, keep_vba=workbook_path.suffix.lower() == ".xlsm")
        for worksheet in workbook.worksheets.values():
            openpyxl_ws = openpyxl_wb[worksheet.name]
            worksheet.fingerprint = self.fingerprinter.fingerprint_worksheet(worksheet, openpyxl_ws)
        self.html_report.generate(workbook)
        return workbook

    def compare(self, old_path: Path, new_path: Path) -> dict[str, Any]:
        """Compare two workbook versions at a basic workbook summary level."""
        old_workbook = self.reader.read(old_path)
        new_workbook = self.reader.read(new_path)
        return {
            "old": old_workbook.name,
            "new": new_workbook.name,
            "worksheet_delta": new_workbook.worksheet_count() - old_workbook.worksheet_count(),
        }

    def package(self, workbook_path: Path) -> str:
        """Create a minimal template artifact preserving the source workbook bytes."""
        template_path = workbook_path.with_suffix(".template")
        template_path.write_bytes(workbook_path.read_bytes())
        return str(template_path)

    def fill(self, template_path: Path, data_path: Path) -> str:
        """Create an output workbook name for a filled template request."""
        data_path.read_text(encoding="utf-8")
        output_path = template_path.with_name(f"Completed_{template_path.stem}.xlsm")
        output_path.write_bytes(template_path.read_bytes())
        return str(output_path)

    def validate(self, template_path: Path) -> dict[str, Any]:
        """Validate that a template artifact exists and is non-empty."""
        errors: list[str] = []
        if not template_path.exists():
            errors.append("Template file does not exist")
        elif template_path.stat().st_size == 0:
            errors.append("Template file is empty")
        return {"valid": not errors, "errors": errors}
