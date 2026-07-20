"""Tests for the Workbook model."""

from pdie.core.cell import Cell
from pdie.core.workbook import Workbook
from pdie.core.worksheet import Worksheet


class TestWorkbook:
    """Tests for Workbook model."""

    def test_workbook_creation(self) -> None:
        """Test creating a workbook."""
        workbook = Workbook(name="Test")
        assert workbook.name == "Test"
        assert workbook.worksheet_count() == 0

    def test_workbook_add_worksheet(self) -> None:
        """Test adding a worksheet to workbook."""
        workbook = Workbook(name="Test")
        worksheet = Worksheet(name="Sheet1", index=0)
        workbook.worksheets[worksheet.name] = worksheet

        assert workbook.worksheet_count() == 1
        assert workbook.get_worksheet("Sheet1") == worksheet

    def test_workbook_get_worksheet_by_index(self) -> None:
        """Test getting worksheet by index."""
        workbook = Workbook(name="Test")
        worksheet = Worksheet(name="Sheet1", index=0)
        workbook.worksheets[worksheet.name] = worksheet

        assert workbook.get_worksheet_by_index(0) == worksheet
        assert workbook.get_worksheet_by_index(1) is None

    def test_workbook_totals(self) -> None:
        """Test total calculations."""
        workbook = Workbook(name="Test")
        worksheet = Worksheet(name="Sheet1", index=0)

        cell1 = Cell(address="A1", row=1, column=1, value="Test")
        cell2 = Cell(address="A2", row=2, column=1, formula="=A1")
        cell3 = Cell(
            address="A3",
            row=3,
            column=1,
            value=42,
            editable_score=0.8,
            locked=False,
        )

        worksheet.cells[cell1.address] = cell1
        worksheet.cells[cell2.address] = cell2
        worksheet.cells[cell3.address] = cell3

        workbook.worksheets[worksheet.name] = worksheet

        assert workbook.total_cells() == 3
        assert workbook.total_formulas() == 1
        assert workbook.total_editable_cells() == 1
