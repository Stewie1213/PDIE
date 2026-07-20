"""Tests for workbook analyzer."""

from pathlib import Path

from pdie.analyzers.workbook_analyzer import WorkbookAnalyzer
from pdie.readers.excel_reader import ExcelReader


class TestWorkbookAnalyzer:
    """Tests for WorkbookAnalyzer."""

    def test_analyze_workbook(self, sample_workbook: Path) -> None:
        """Test analyzing a workbook."""
        workbook = ExcelReader.read(sample_workbook)
        WorkbookAnalyzer.analyze_workbook(workbook)

        # Check that worksheets were analyzed
        for worksheet in workbook.worksheets.values():
            # At least some cells should have metadata
            analyzed_cells = [
                c for c in worksheet.cells.values() if c.metadata
            ]
            assert len(analyzed_cells) > 0

    def test_get_summary(self, sample_workbook: Path) -> None:
        """Test getting workbook summary."""
        workbook = ExcelReader.read(sample_workbook)
        WorkbookAnalyzer.analyze_workbook(workbook)

        summary = WorkbookAnalyzer.get_summary(workbook)

        assert summary["workbook_name"] == "sample"
        assert summary["worksheet_count"] == 1
        assert summary["total_cells"] > 0
        assert "Sheet1" in summary["worksheets"]

    def test_summary_worksheet_details(self, sample_workbook: Path) -> None:
        """Test that summary includes worksheet details."""
        workbook = ExcelReader.read(sample_workbook)
        WorkbookAnalyzer.analyze_workbook(workbook)

        summary = WorkbookAnalyzer.get_summary(workbook)
        ws_summary = summary["worksheets"]["Sheet1"]

        assert ws_summary["name"] == "Sheet1"
        assert ws_summary["index"] == 0
        assert ws_summary["cell_count"] > 0
        assert "field_type_counts" in ws_summary
        assert "data_region" in ws_summary

    def test_summary_with_fingerprint(self, temp_dir: Path) -> None:
        """Test that summary includes fingerprint info if available."""
        from pdie.core.cell import Cell
        from pdie.core.fingerprint import (
            WorkbookFingerprint,
            WorksheetFingerprint,
        )
        from pdie.core.workbook import Workbook
        from pdie.core.worksheet import Worksheet

        workbook = Workbook(name="test", file_path=temp_dir / "test.xlsx")
        worksheet = Worksheet(name="Sheet1", index=0)

        cell = Cell(address="A1", row=1, column=1, value="Data")
        worksheet.cells[cell.address] = cell
        workbook.worksheets[worksheet.name] = worksheet

        # Add fingerprints
        workbook.fingerprint = WorkbookFingerprint(
            workbook_name="test",
            file_type=".xlsx",
            worksheet_count=1,
        )
        worksheet.fingerprint = WorksheetFingerprint(
            name="Sheet1", rows=10, columns=5
        )

        WorkbookAnalyzer.analyze_workbook(workbook)
        summary = WorkbookAnalyzer.get_summary(workbook)

        assert "fingerprint" in summary
        assert summary["fingerprint"]["file_type"] == ".xlsx"
        assert "fingerprint" in summary["worksheets"]["Sheet1"]
        assert summary["worksheets"]["Sheet1"]["fingerprint"]["rows"] == 10

    def test_summary_field_type_counts(self, temp_dir: Path) -> None:
        """Test that field type counts are included in summary."""
        from pdie.core.cell import Cell
        from pdie.core.workbook import Workbook
        from pdie.core.worksheet import Worksheet

        workbook = Workbook(name="test")
        worksheet = Worksheet(name="Sheet1", index=0)

        # Add cells of different types
        text_cell = Cell(address="A1", row=1, column=1, value="Text")
        number_cell = Cell(
            address="B1", row=1, column=2, value=42, data_type="n"
        )

        worksheet.cells[text_cell.address] = text_cell
        worksheet.cells[number_cell.address] = number_cell
        workbook.worksheets[worksheet.name] = worksheet

        WorkbookAnalyzer.analyze_workbook(workbook)
        summary = WorkbookAnalyzer.get_summary(workbook)

        ws_summary = summary["worksheets"]["Sheet1"]
        assert "field_type_counts" in ws_summary
        assert len(ws_summary["field_type_counts"]) > 0
