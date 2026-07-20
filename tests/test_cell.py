"""Tests for the Cell model."""

from pdie.core.cell import Cell


class TestCell:
    """Tests for Cell model."""

    def test_cell_creation(self) -> None:
        """Test creating a cell."""
        cell = Cell(address="A1", row=1, column=1, value="Test")
        assert cell.address == "A1"
        assert cell.row == 1
        assert cell.column == 1
        assert cell.value == "Test"

    def test_cell_is_formula(self) -> None:
        """Test formula detection."""
        cell_with_formula = Cell(address="A1", row=1, column=1, formula="=B1+B2")
        cell_without_formula = Cell(address="A2", row=2, column=1, value=42)

        assert cell_with_formula.is_formula()
        assert not cell_without_formula.is_formula()

    def test_cell_is_editable(self) -> None:
        """Test editable detection."""
        editable_cell = Cell(address="A1", row=1, column=1, editable_score=0.8, locked=False)
        locked_cell = Cell(address="A2", row=2, column=1, editable_score=0.8, locked=True)
        uneditable_cell = Cell(address="A3", row=3, column=1, editable_score=0.3, locked=False)

        assert editable_cell.is_editable()
        assert not locked_cell.is_editable()
        assert not uneditable_cell.is_editable()

    def test_cell_display_value(self) -> None:
        """Test display value."""
        cell_with_value = Cell(address="A1", row=1, column=1, value="Test")
        cell_without_value = Cell(address="A2", row=2, column=1)

        assert cell_with_value.get_display_value() == "Test"
        assert cell_without_value.get_display_value() == ""
