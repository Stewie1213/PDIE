"""Cell model representing a single cell in a worksheet."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Cell:
    """Represents a single cell in a worksheet."""

    address: str
    row: int
    column: int
    value: Any = None
    formula: Optional[str] = None
    data_type: Optional[str] = None
    fill: Optional[str] = None
    border: Optional[str] = None
    font_name: Optional[str] = None
    font_size: Optional[int] = None
    bold: bool = False
    italic: bool = False
    locked: bool = True
    hidden: bool = False
    merged: bool = False
    validation: Optional[str] = None
    hyperlink: Optional[str] = None
    comment: Optional[str] = None
    number_format: Optional[str] = None
    editable_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_formula(self) -> bool:
        """Check if cell contains a formula."""
        return self.formula is not None and self.formula.startswith("=")

    def is_editable(self) -> bool:
        """Check if cell is editable based on score."""
        return self.editable_score > 0.5 and not self.locked

    def has_validation(self) -> bool:
        """Check if cell has data validation."""
        return self.validation is not None

    def get_display_value(self) -> str:
        """Get the display value of the cell."""
        if self.value is None:
            return ""
        return str(self.value)
