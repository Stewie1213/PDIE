"""Analyzer for individual cells."""

import re
from typing import Optional

from pdie.core.cell import Cell
from pdie.core.worksheet import Worksheet


class FieldType:
    """Field type constants."""

    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    BOOLEAN = "boolean"
    FORMULA = "formula"
    DROPDOWN = "dropdown"
    UNKNOWN = "unknown"


class CellAnalyzer:
    """Analyzes individual cells to detect field types and properties."""

    @staticmethod
    def analyze_cell(cell: Cell, worksheet: Worksheet) -> None:
        """Analyze a cell and update its properties.

        Args:
            cell: The cell to analyze.
            worksheet: The worksheet containing the cell.
        """
        # Detect field type
        cell.metadata["field_type"] = CellAnalyzer._detect_field_type(cell)

        # Detect if field is likely editable
        editable_score = CellAnalyzer._calculate_editable_score(cell, worksheet)
        cell.editable_score = editable_score

        # Try to detect field name from surrounding cells
        field_name = CellAnalyzer._detect_field_name(cell, worksheet)
        if field_name:
            cell.metadata["field_name"] = field_name

        # Detect if required
        is_required = CellAnalyzer._detect_required(cell, worksheet)
        cell.metadata["required"] = is_required

        # Detect max length for text fields
        if cell.metadata["field_type"] == FieldType.TEXT:
            max_length = CellAnalyzer._detect_max_length(cell)
            if max_length:
                cell.metadata["max_length"] = max_length

    @staticmethod
    def _detect_field_type(cell: Cell) -> str:
        """Detect the field type of a cell.

        Args:
            cell: The cell to analyze.

        Returns:
            str: The field type.
        """
        if cell.is_formula():
            return FieldType.FORMULA

        if cell.has_validation():
            return FieldType.DROPDOWN

        if cell.data_type == "d":
            return FieldType.DATE

        if cell.data_type == "n":
            return CellAnalyzer._detect_numeric_field_type(cell)

        if cell.data_type == "b":
            return FieldType.BOOLEAN

        if cell.value is None:
            return FieldType.UNKNOWN

        # Try to detect from value
        value_str = str(cell.value).strip().lower()

        if value_str in ("true", "false", "yes", "no"):
            return FieldType.BOOLEAN

        # Check for currency symbol
        if re.search(r"[\$¥€]", str(cell.value)):
            return FieldType.CURRENCY

        # Try to parse as number
        try:
            float(str(cell.value))
            return FieldType.NUMBER
        except (ValueError, TypeError):
            pass

        # Default to text
        return FieldType.TEXT

    @staticmethod
    def _detect_numeric_field_type(cell: Cell) -> str:
        """Detect the field type for numeric cells using number format hints."""
        if cell.number_format:
            fmt_lower = cell.number_format.lower()
            if "$" in fmt_lower or "¥" in fmt_lower or "€" in fmt_lower:
                return FieldType.CURRENCY
            if "%" in fmt_lower:
                return FieldType.PERCENTAGE
        return FieldType.NUMBER

    @staticmethod
    def _calculate_editable_score(cell: Cell, worksheet: Worksheet) -> float:
        """Calculate the editability score for a cell.

        Args:
            cell: The cell to analyze.
            worksheet: The worksheet containing the cell.

        Returns:
            float: Editable score (0.0 to 1.0).
        """
        score = 0.0

        # Locked cells are not editable
        if cell.locked:
            return 0.0

        # Hidden cells are not editable
        if cell.hidden:
            return 0.0

        # Formulas are not editable (users shouldn't edit them)
        if cell.is_formula():
            return 0.0

        # Cells with validation (dropdowns) are editable
        if cell.has_validation():
            score += 0.8

        # Cells with specific data types are more likely editable
        field_type = CellAnalyzer._detect_field_type(cell)
        if field_type in (
            FieldType.TEXT,
            FieldType.NUMBER,
            FieldType.DATE,
            FieldType.CURRENCY,
        ):
            score = max(score, 0.6)

        # Check for label-like content (headers, etc.)
        if CellAnalyzer._is_label_like(cell, worksheet):
            score = 0.1

        return min(score, 1.0)

    @staticmethod
    def _is_label_like(cell: Cell, worksheet: Worksheet) -> bool:
        """Determine if a cell looks like a label or header.

        Args:
            cell: The cell to check.
            worksheet: The worksheet containing the cell.

        Returns:
            bool: True if cell looks like a label.
        """
        # Locked cells in the first row are commonly headers. Unlocked first-row
        # cells can still be legitimate inputs in compact forms.
        if cell.row == 1 and cell.locked:
            return True

        # Check if text is short and non-numeric. Unlocked cells are usually
        # inputs, so avoid classifying them as labels based only on brevity.
        if cell.locked and cell.value and isinstance(cell.value, str):
            value_str = str(cell.value).strip()
            if len(value_str) < 3:
                return True
            if len(value_str.split()) == 1 and len(value_str) < 15:
                row_cells = worksheet.get_row(cell.row)
                if len(row_cells) <= 2:
                    return True

        # Bold text often indicates labels
        if cell.bold and cell.row <= 5:
            return True

        return False

    @staticmethod
    def _detect_field_name(cell: Cell, worksheet: Worksheet) -> Optional[str]:
        """Try to detect the field name from surrounding cells.

        Args:
            cell: The cell to analyze.
            worksheet: The worksheet containing the cell.

        Returns:
            Optional[str]: The detected field name, or None.
        """
        # Check if cell is below a header
        if cell.row > 1:
            header_cell = worksheet.get_cell(f"{CellAnalyzer._col_index_to_letter(cell.column)}{1}")
            if header_cell and header_cell.value:
                return str(header_cell.value).strip()

        # Check if cell is to the right of a label
        if cell.column > 1:
            label_cell = worksheet.get_cell(
                f"{CellAnalyzer._col_index_to_letter(cell.column - 1)}{cell.row}"
            )
            if (
                label_cell
                and label_cell.value
                and CellAnalyzer._is_label_like(label_cell, worksheet)
            ):
                return str(label_cell.value).strip()

        return None

    @staticmethod
    def _detect_required(cell: Cell, worksheet: Worksheet) -> bool:
        """Determine if a field is required.

        Args:
            cell: The cell to analyze.
            worksheet: The worksheet containing the cell.

        Returns:
            bool: True if field appears required.
        """
        # Check for validation with no empty option
        if cell.has_validation() and cell.validation:
            if "empty" not in cell.validation.lower():
                return True

        # Check if there's a required indicator nearby
        # Look for asterisk in label
        field_name = CellAnalyzer._detect_field_name(cell, worksheet)
        if field_name and "*" in field_name:
            return True

        return False

    @staticmethod
    def _detect_max_length(cell: Cell) -> Optional[int]:
        """Detect maximum length for text fields.

        Args:
            cell: The cell to analyze.

        Returns:
            Optional[int]: Maximum length, or None if not detected.
        """
        # Check number format for length hints
        if cell.number_format:
            # Extract digit patterns that might indicate length
            match = re.search(r"\d{2,}", cell.number_format)
            if match:
                return int(match.group())

        # Check cell value length as hint
        if cell.value and isinstance(cell.value, str):
            value_len = len(str(cell.value))
            if value_len > 0:
                # Round up to nearest 10
                return ((value_len // 10) + 1) * 10

        return None

    @staticmethod
    def _col_index_to_letter(col_num: int) -> str:
        """Convert column number to letter.

        Args:
            col_num: Column number (1-based).

        Returns:
            str: Column letter(s).
        """
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(col_num % 26 + ord("A")) + result
            col_num //= 26
        return result
