"""Workbook model representing an Excel file."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pdie.core.fingerprint import WorkbookFingerprint
from pdie.core.worksheet import Worksheet


@dataclass
class Workbook:
    """Represents an Excel workbook."""

    name: str
    file_path: Optional[Path] = None
    worksheets: dict[str, Worksheet] = field(default_factory=dict)
    fingerprint: Optional[WorkbookFingerprint] = None
    metadata: dict = field(default_factory=dict)

    def get_worksheet(self, name: str) -> Optional[Worksheet]:
        """Get a worksheet by name."""
        return self.worksheets.get(name)

    def get_worksheet_by_index(self, index: int) -> Optional[Worksheet]:
        """Get a worksheet by index."""
        for ws in self.worksheets.values():
            if ws.index == index:
                return ws
        return None

    def worksheet_count(self) -> int:
        """Get the total number of worksheets."""
        return len(self.worksheets)

    def total_cells(self) -> int:
        """Get the total number of cells across all worksheets."""
        return sum(ws.cell_count() for ws in self.worksheets.values())

    def total_formulas(self) -> int:
        """Get the total number of formulas across all worksheets."""
        return sum(ws.formula_count() for ws in self.worksheets.values())

    def total_editable_cells(self) -> int:
        """Get the total number of editable cells across all worksheets."""
        return sum(ws.editable_count() for ws in self.worksheets.values())
