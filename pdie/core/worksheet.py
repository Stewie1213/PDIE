"""Worksheet model representing a sheet in a workbook."""

from dataclasses import dataclass, field
from typing import Optional

from pdie.core.cell import Cell
from pdie.core.fingerprint import WorksheetFingerprint


@dataclass
class Worksheet:
    """Represents a single worksheet in a workbook."""

    name: str
    index: int
    cells: dict[str, Cell] = field(default_factory=dict)
    hidden: bool = False
    protected: bool = False
    fingerprint: Optional[WorksheetFingerprint] = None
    metadata: dict = field(default_factory=dict)

    def get_cell(self, address: str) -> Optional[Cell]:
        """Get a cell by its address (e.g., 'A1')."""
        return self.cells.get(address.upper())

    def get_row(self, row_num: int) -> list[Cell]:
        """Get all cells in a row."""
        return [c for c in self.cells.values() if c.row == row_num]

    def get_column(self, col_num: int) -> list[Cell]:
        """Get all cells in a column."""
        return [c for c in self.cells.values() if c.column == col_num]

    def cell_count(self) -> int:
        """Get the total number of cells."""
        return len(self.cells)

    def formula_count(self) -> int:
        """Get the number of cells with formulas."""
        return sum(1 for c in self.cells.values() if c.is_formula())

    def editable_count(self) -> int:
        """Get the number of editable cells."""
        return sum(1 for c in self.cells.values() if c.is_editable())
