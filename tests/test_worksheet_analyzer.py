"""Tests for worksheet analyzer."""

from pdie.analyzers.cell_analyzer import FieldType
from pdie.analyzers.worksheet_analyzer import WorksheetAnalyzer
from pdie.core.cell import Cell
from pdie.core.worksheet import Worksheet


class TestWorksheetAnalyzer:
    """Tests for WorksheetAnalyzer."""

    def test_analyze_worksheet(self) -> None:
        """Test analyzing a worksheet."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell1 = Cell(address="A1", row=1, column=1, value="Name")
        cell2 = Cell(address="A2", row=2, column=1, value="John", locked=False)
        cell3 = Cell(address="B2", row=2, column=2, value=30, data_type="n", locked=False)

        worksheet.cells[cell1.address] = cell1
        worksheet.cells[cell2.address] = cell2
        worksheet.cells[cell3.address] = cell3

        WorksheetAnalyzer.analyze_worksheet(worksheet)

        # Check that all cells were analyzed
        assert cell1.metadata.get("field_type") is not None
        assert cell2.metadata.get("field_type") is not None
        assert cell3.metadata.get("field_type") is not None

    def test_detect_header_row(self) -> None:
        """Test detecting header row."""
        worksheet = Worksheet(name="Sheet1", index=0)

        # Add header row
        header1 = Cell(address="A1", row=1, column=1, value="Name")
        header2 = Cell(address="B1", row=1, column=2, value="Age")
        header3 = Cell(address="C1", row=1, column=3, value="Email")

        # Add data rows
        data1 = Cell(address="A2", row=2, column=1, value="John")
        data2 = Cell(address="B2", row=2, column=2, value=30)
        data3 = Cell(address="C2", row=2, column=3, value="john@example.com")

        worksheet.cells[header1.address] = header1
        worksheet.cells[header2.address] = header2
        worksheet.cells[header3.address] = header3
        worksheet.cells[data1.address] = data1
        worksheet.cells[data2.address] = data2
        worksheet.cells[data3.address] = data3

        header_row = WorksheetAnalyzer.detect_header_row(worksheet)

        assert header_row == 1

    def test_detect_data_region(self) -> None:
        """Test detecting data region."""
        worksheet = Worksheet(name="Sheet1", index=0)

        cell1 = Cell(address="A1", row=1, column=1, value="Data")
        cell2 = Cell(address="C3", row=3, column=3, value="Data")

        worksheet.cells[cell1.address] = cell1
        worksheet.cells[cell2.address] = cell2

        min_row, min_col, max_row, max_col = WorksheetAnalyzer.detect_data_region(worksheet)

        assert min_row == 1
        assert min_col == 1
        assert max_row == 3
        assert max_col == 3

    def test_count_by_field_type(self) -> None:
        """Test counting cells by field type."""
        worksheet = Worksheet(name="Sheet1", index=0)

        cell1 = Cell(address="A1", row=1, column=1, value="Text")
        cell2 = Cell(address="A2", row=2, column=1, value=42, data_type="n")
        cell3 = Cell(address="A3", row=3, column=1, value="Text2")

        worksheet.cells[cell1.address] = cell1
        worksheet.cells[cell2.address] = cell2
        worksheet.cells[cell3.address] = cell3

        # Analyze first
        WorksheetAnalyzer.analyze_worksheet(worksheet)

        counts = WorksheetAnalyzer.count_by_field_type(worksheet)

        assert counts.get(FieldType.TEXT, 0) >= 2
        assert counts.get(FieldType.NUMBER, 0) >= 1

    def test_get_editable_cells(self) -> None:
        """Test getting editable cells."""
        worksheet = Worksheet(name="Sheet1", index=0)

        editable = Cell(address="A1", row=1, column=1, value="Edit", locked=False)
        locked = Cell(address="A2", row=2, column=1, value="No Edit", locked=True)

        worksheet.cells[editable.address] = editable
        worksheet.cells[locked.address] = locked

        # Analyze first to set editable scores
        WorksheetAnalyzer.analyze_worksheet(worksheet)

        editable_cells = WorksheetAnalyzer.get_editable_cells(worksheet)

        assert len(editable_cells) >= 1
        assert locked not in editable_cells  # locked cells excluded

    def test_get_formula_cells(self) -> None:
        """Test getting formula cells."""
        worksheet = Worksheet(name="Sheet1", index=0)

        formula_cell = Cell(address="A1", row=1, column=1, formula="=B1+B2", value=10)
        regular_cell = Cell(address="A2", row=2, column=1, value="Data")

        worksheet.cells[formula_cell.address] = formula_cell
        worksheet.cells[regular_cell.address] = regular_cell

        formula_cells = WorksheetAnalyzer.get_formula_cells(worksheet)

        assert len(formula_cells) == 1
        assert formula_cell in formula_cells

    def test_get_validation_cells(self) -> None:
        """Test getting validation cells."""
        worksheet = Worksheet(name="Sheet1", index=0)

        dropdown_cell = Cell(
            address="A1",
            row=1,
            column=1,
            value="Option1",
            validation="Option1,Option2",
        )
        regular_cell = Cell(address="A2", row=2, column=1, value="Data")

        worksheet.cells[dropdown_cell.address] = dropdown_cell
        worksheet.cells[regular_cell.address] = regular_cell

        validation_cells = WorksheetAnalyzer.get_validation_cells(worksheet)

        assert len(validation_cells) == 1
        assert dropdown_cell in validation_cells
