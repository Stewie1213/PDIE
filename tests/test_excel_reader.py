"""Tests for the Excel reader."""

from pathlib import Path

import pytest

from pdie.readers.excel_reader import ExcelReader


class TestExcelReader:
    """Tests for ExcelReader."""

    def test_read_valid_workbook(self, sample_workbook: Path) -> None:
        """Test reading a valid Excel workbook."""
        workbook = ExcelReader.read(sample_workbook)
        assert workbook.name == "sample"
        assert workbook.worksheet_count() == 1
        assert "Sheet1" in workbook.worksheets

    def test_read_worksheet(self, sample_workbook: Path) -> None:
        """Test that worksheets are read correctly."""
        workbook = ExcelReader.read(sample_workbook)
        worksheet = workbook.get_worksheet("Sheet1")
        assert worksheet is not None
        assert worksheet.name == "Sheet1"
        assert worksheet.cell_count() >= 4

    def test_read_cells(self, sample_workbook: Path) -> None:
        """Test that cells are read correctly."""
        workbook = ExcelReader.read(sample_workbook)
        worksheet = workbook.get_worksheet("Sheet1")
        assert worksheet is not None

        cell_a1 = worksheet.get_cell("A1")
        assert cell_a1 is not None
        assert cell_a1.value == "Name"

        cell_b2 = worksheet.get_cell("B2")
        assert cell_b2 is not None
        assert cell_b2.value == 123

    def test_read_formula(self, sample_workbook: Path) -> None:
        """Test that formulas are detected."""
        workbook = ExcelReader.read(sample_workbook)
        worksheet = workbook.get_worksheet("Sheet1")
        assert worksheet is not None

        cell_b3 = worksheet.get_cell("B3")
        assert cell_b3 is not None
        assert cell_b3.formula == "=B2*2"

    def test_read_nonexistent_file(self) -> None:
        """Test reading a non-existent file."""
        with pytest.raises(FileNotFoundError):
            ExcelReader.read(Path("/nonexistent/file.xlsx"))

    def test_read_invalid_file(self, temp_dir: Path) -> None:
        """Test reading an invalid Excel file."""
        invalid_file = temp_dir / "invalid.xlsx"
        invalid_file.write_text("This is not an Excel file")

        with pytest.raises(ValueError):
            ExcelReader.read(invalid_file)
