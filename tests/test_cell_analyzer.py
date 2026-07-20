"""Tests for cell analyzer."""

from pdie.analyzers.cell_analyzer import CellAnalyzer, FieldType
from pdie.core.cell import Cell
from pdie.core.worksheet import Worksheet


class TestCellAnalyzer:
    """Tests for CellAnalyzer."""

    def test_analyze_text_cell(self) -> None:
        """Test analyzing a text cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(address="A1", row=1, column=1, value="Hello")

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.TEXT

    def test_analyze_number_cell(self) -> None:
        """Test analyzing a number cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(address="A1", row=1, column=1, value=42, data_type="n")

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.NUMBER

    def test_analyze_currency_cell(self) -> None:
        """Test analyzing a currency cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(
            address="A1",
            row=1,
            column=1,
            value=99.99,
            data_type="n",
            number_format="$#,##0.00",
        )

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.CURRENCY

    def test_analyze_percentage_cell(self) -> None:
        """Test analyzing a percentage cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(
            address="A1",
            row=1,
            column=1,
            value=0.75,
            data_type="n",
            number_format="0%",
        )

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.PERCENTAGE

    def test_analyze_date_cell(self) -> None:
        """Test analyzing a date cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(
            address="A1",
            row=1,
            column=1,
            value="2024-01-01",
            data_type="d",
        )

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.DATE

    def test_analyze_boolean_cell(self) -> None:
        """Test analyzing a boolean cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(address="A1", row=1, column=1, value=True, data_type="b")

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.BOOLEAN

    def test_analyze_formula_cell(self) -> None:
        """Test analyzing a formula cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(address="A1", row=1, column=1, formula="=B1+B2", value=10)

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.FORMULA

    def test_analyze_dropdown_cell(self) -> None:
        """Test analyzing a dropdown cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(
            address="A1",
            row=1,
            column=1,
            value="Option1",
            validation="Option1,Option2,Option3",
        )

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.metadata["field_type"] == FieldType.DROPDOWN

    def test_editable_score_locked_cell(self) -> None:
        """Test editable score for locked cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(
            address="A1",
            row=2,
            column=1,
            value="Data",
            locked=True,
        )

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.editable_score == 0.0

    def test_editable_score_formula_cell(self) -> None:
        """Test editable score for formula cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(
            address="A1",
            row=2,
            column=1,
            formula="=B1*2",
            locked=False,
        )

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.editable_score == 0.0

    def test_editable_score_text_cell(self) -> None:
        """Test editable score for text cell."""
        worksheet = Worksheet(name="Sheet1", index=0)
        cell = Cell(
            address="A1",
            row=2,
            column=1,
            value="Input",
            locked=False,
        )

        CellAnalyzer.analyze_cell(cell, worksheet)

        assert cell.editable_score > 0.5

    def test_detect_field_name_from_header(self) -> None:
        """Test detecting field name from header."""
        worksheet = Worksheet(name="Sheet1", index=0)
        header_cell = Cell(address="A1", row=1, column=1, value="Name")
        data_cell = Cell(address="A2", row=2, column=1, value="John")

        worksheet.cells[header_cell.address] = header_cell
        worksheet.cells[data_cell.address] = data_cell

        CellAnalyzer.analyze_cell(data_cell, worksheet)

        assert data_cell.metadata.get("field_name") == "Name"

    def test_col_index_to_letter(self) -> None:
        """Test column index to letter conversion."""
        assert CellAnalyzer._col_index_to_letter(1) == "A"
        assert CellAnalyzer._col_index_to_letter(26) == "Z"
        assert CellAnalyzer._col_index_to_letter(27) == "AA"
        assert CellAnalyzer._col_index_to_letter(52) == "AZ"
        assert CellAnalyzer._col_index_to_letter(702) == "ZZ"
