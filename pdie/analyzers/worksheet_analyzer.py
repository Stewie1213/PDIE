"""Analyzer for worksheets."""

from pdie.analyzers.cell_analyzer import CellAnalyzer
from pdie.core.worksheet import Worksheet


class WorksheetAnalyzer:
    """Analyzes worksheets and their cells."""

    @staticmethod
    def analyze_worksheet(worksheet: Worksheet) -> None:
        """Analyze all cells in a worksheet.

        Args:
            worksheet: The worksheet to analyze.
        """
        # Analyze each cell
        for cell in worksheet.cells.values():
            CellAnalyzer.analyze_cell(cell, worksheet)

    @staticmethod
    def detect_header_row(worksheet: Worksheet) -> int:
        """Detect which row contains headers.

        Args:
            worksheet: The worksheet to analyze.

        Returns:
            int: The row number (1-based) that appears to be headers, or 0 if none found.
        """
        # Check first 5 rows for header patterns
        for row_num in range(1, min(6, worksheet.cell_count() + 1)):
            row_cells = worksheet.get_row(row_num)
            if not row_cells:
                continue

            # Count how many cells look like headers
            header_count = 0
            for cell in row_cells:
                if cell.value and isinstance(cell.value, str):
                    value_str = str(cell.value).strip()
                    # Headers are typically short, non-numeric text
                    if 1 < len(value_str) < 50:
                        if not value_str.isdigit():
                            header_count += 1

            # If most cells in row look like headers, it's the header row
            if header_count > 0 and header_count >= len(row_cells) * 0.7:
                return row_num

        return 0

    @staticmethod
    def detect_data_region(
        worksheet: Worksheet,
    ) -> tuple[int, int, int, int]:
        """Detect the data region (min_row, min_col, max_row, max_col).

        Args:
            worksheet: The worksheet to analyze.

        Returns:
            tuple: (min_row, min_col, max_row, max_col) or (0, 0, 0, 0) if empty.
        """
        if not worksheet.cells:
            return (0, 0, 0, 0)

        rows = [cell.row for cell in worksheet.cells.values()]
        cols = [cell.column for cell in worksheet.cells.values()]

        return (min(rows), min(cols), max(rows), max(cols))

    @staticmethod
    def count_by_field_type(worksheet: Worksheet) -> dict[str, int]:
        """Count cells by field type.

        Args:
            worksheet: The worksheet to analyze.

        Returns:
            dict: Field type counts.
        """
        counts: dict[str, int] = {}

        for cell in worksheet.cells.values():
            field_type = cell.metadata.get("field_type", "unknown")
            counts[field_type] = counts.get(field_type, 0) + 1

        return counts

    @staticmethod
    def get_editable_cells(worksheet: Worksheet) -> list:
        """Get all editable cells in a worksheet.

        Args:
            worksheet: The worksheet to analyze.

        Returns:
            list: List of editable cells.
        """
        return [cell for cell in worksheet.cells.values() if cell.is_editable()]

    @staticmethod
    def get_formula_cells(worksheet: Worksheet) -> list:
        """Get all formula cells in a worksheet.

        Args:
            worksheet: The worksheet to analyze.

        Returns:
            list: List of formula cells.
        """
        return [cell for cell in worksheet.cells.values() if cell.is_formula()]

    @staticmethod
    def get_validation_cells(worksheet: Worksheet) -> list:
        """Get all cells with data validation in a worksheet.

        Args:
            worksheet: The worksheet to analyze.

        Returns:
            list: List of cells with validation.
        """
        return [cell for cell in worksheet.cells.values() if cell.has_validation()]
