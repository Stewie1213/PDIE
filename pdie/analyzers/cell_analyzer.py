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
        """Analyze a cell and update its properties."""
        cell.metadata["field_type"] = CellAnalyzer._detect_field_type(cell)
        cell.editable_score = CellAnalyzer._calculate_editable_score(cell, worksheet)
        field_name = CellAnalyzer._detect_field_name(cell, worksheet)
        if field_name:
            cell.metadata["field_name"] = field_name
        cell.metadata["required"] = CellAnalyzer._detect_required(cell, worksheet)
        if cell.metadata["field_type"] == FieldType.TEXT:
            max_length = CellAnalyzer._detect_max_length(cell)
            if max_length:
                cell.metadata["max_length"] = max_length

    @staticmethod
    def _detect_field_type(cell: Cell) -> str:
        """Detect the field type of a cell."""
        if cell.is_formula():
            return FieldType.FORMULA
        if cell.has_validation():
            return FieldType.DROPDOWN
        if cell.data_type == "d":
            return FieldType.DATE
        if cell.data_type == "n":
            return CellAnalyzer._numeric_type(cell)
        if cell.data_type == "b":
            return FieldType.BOOLEAN
        if cell.value is None:
            return FieldType.UNKNOWN
        return CellAnalyzer._type_from_value(cell.value)

    @staticmethod
    def _numeric_type(cell: Cell) -> str:
        if cell.number_format:
            fmt_lower = cell.number_format.lower()
            if any(symbol in fmt_lower for symbol in ("$", "¥", "€")):
                return FieldType.CURRENCY
            if "%" in fmt_lower:
                return FieldType.PERCENTAGE
        return FieldType.NUMBER

    @staticmethod
    def _type_from_value(value: object) -> str:
        value_str = str(value).strip().lower()
        if value_str in ("true", "false", "yes", "no"):
            return FieldType.BOOLEAN
        if re.match(r"^[\$¥€].+|.+[\$¥€]$", str(value)):
            return FieldType.CURRENCY
        try:
            float(str(value))
            return FieldType.NUMBER
        except (ValueError, TypeError):
            return FieldType.TEXT

    @staticmethod
    def _calculate_editable_score(cell: Cell, worksheet: Worksheet) -> float:
        """Calculate the editability score for a cell."""
        if cell.locked or cell.hidden or cell.is_formula():
            return 0.0
        score = 0.8 if cell.has_validation() else 0.0
        field_type = CellAnalyzer._detect_field_type(cell)
        if field_type in {FieldType.TEXT, FieldType.NUMBER, FieldType.DATE, FieldType.CURRENCY}:
            score = max(score, 0.6)
        if CellAnalyzer._is_label_like(cell, worksheet):
            score = 0.1
        return min(score, 1.0)

    @staticmethod
    def _is_label_like(cell: Cell, worksheet: Worksheet) -> bool:
        """Determine if a cell looks like a label or header."""
        if cell.row == 1 and cell.locked:
            return True
        if cell.locked and cell.value and isinstance(cell.value, str):
            value_str = str(cell.value).strip()
            if len(value_str) < 3:
                return True
            if len(value_str.split()) == 1 and len(value_str) < 15:
                return len(worksheet.get_row(cell.row)) <= 2
        return bool(cell.bold and cell.row <= 5)

    @staticmethod
    def _detect_field_name(cell: Cell, worksheet: Worksheet) -> Optional[str]:
        """Try to detect the field name from surrounding cells."""
        if cell.row > 1:
            header_cell = worksheet.get_cell(f"{CellAnalyzer._col_index_to_letter(cell.column)}1")
            if header_cell and header_cell.value:
                return str(header_cell.value).strip()
        if cell.column > 1:
            label_cell = worksheet.get_cell(
                f"{CellAnalyzer._col_index_to_letter(cell.column - 1)}{cell.row}"
            )
            if label_cell and label_cell.value and CellAnalyzer._is_label_like(label_cell, worksheet):
                return str(label_cell.value).strip()
        return None

    @staticmethod
    def _detect_required(cell: Cell, worksheet: Worksheet) -> bool:
        """Determine if a field is required."""
        if cell.has_validation() and cell.validation and "empty" not in cell.validation.lower():
            return True
        field_name = CellAnalyzer._detect_field_name(cell, worksheet)
        return bool(field_name and "*" in field_name)

    @staticmethod
    def _detect_max_length(cell: Cell) -> Optional[int]:
        """Detect maximum length for text fields."""
        if cell.number_format:
            match = re.search(r"\d{2,}", cell.number_format)
            if match:
                return int(match.group())
        if cell.value and isinstance(cell.value, str):
            return ((len(str(cell.value)) // 10) + 1) * 10
        return None

    @staticmethod
    def _col_index_to_letter(col_num: int) -> str:
        """Convert column number to letter."""
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(col_num % 26 + ord("A")) + result
            col_num //= 26
        return result
