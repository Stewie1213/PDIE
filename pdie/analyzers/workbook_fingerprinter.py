"""Fingerprinting engine for workbooks."""

import re
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet as OpenpyxlWorksheet

from pdie.core.fingerprint import WorkbookFingerprint, WorksheetFingerprint
from pdie.core.workbook import Workbook
from pdie.core.worksheet import Worksheet


class WorkbookFingerprinter:
    """Generates fingerprints for workbooks and worksheets."""

    @staticmethod
    def fingerprint_workbook(workbook: Workbook) -> WorkbookFingerprint:
        """Generate a fingerprint for a workbook."""
        if not workbook.file_path:
            raise ValueError("Workbook must have file_path set")
        openpyxl_wb = load_workbook(workbook.file_path, keep_vba=_keeps_vba(workbook.file_path))
        dropdown_count = WorkbookFingerprinter._dropdown_count(openpyxl_wb, workbook)
        merged_range_count = WorkbookFingerprinter._merged_range_count(openpyxl_wb, workbook)
        contains_images = any(getattr(openpyxl_wb[ws.name], "_images", []) for ws in workbook.worksheets.values())
        contains_tables = any(getattr(openpyxl_wb[ws.name], "_tables", []) for ws in workbook.worksheets.values())
        return WorkbookFingerprint(
            workbook_name=workbook.name,
            file_type=workbook.file_path.suffix.lower(),
            worksheet_count=workbook.worksheet_count(),
            contains_macros=workbook.file_path.suffix.lower() in (".xlsm", ".xltm"),
            contains_images=contains_images,
            contains_tables=contains_tables,
            dropdown_count=dropdown_count,
            formula_count=workbook.total_formulas(),
            merged_range_count=merged_range_count,
            named_range_count=len(openpyxl_wb.defined_names),
            protected=bool(openpyxl_wb.security.lockStructure or openpyxl_wb.security.lockWindows),
        )

    @staticmethod
    def _dropdown_count(openpyxl_wb, workbook: Workbook) -> int:
        count = 0
        for worksheet in workbook.worksheets.values():
            count += len(openpyxl_wb[worksheet.name].data_validations.dataValidation)
        return count

    @staticmethod
    def _merged_range_count(openpyxl_wb, workbook: Workbook) -> int:
        return sum(len(openpyxl_wb[worksheet.name].merged_cells.ranges) for worksheet in workbook.worksheets.values())

    @staticmethod
    def fingerprint_worksheet(worksheet: Worksheet, openpyxl_ws: OpenpyxlWorksheet) -> WorksheetFingerprint:
        """Generate a fingerprint for a worksheet."""
        max_row, max_col = WorkbookFingerprinter._dimensions(openpyxl_ws)
        return WorksheetFingerprint(
            name=worksheet.name,
            rows=max_row,
            columns=max_col,
            merged_cells=len(openpyxl_ws.merged_cells.ranges),
            formula_cells=worksheet.formula_count(),
            tables=len(openpyxl_ws._tables) if openpyxl_ws._tables else 0,
            images=len(openpyxl_ws._images) if openpyxl_ws._images else 0,
            hidden=worksheet.hidden,
            color_counts=WorkbookFingerprinter._count_colors(worksheet),
            named_regions=len(openpyxl_ws.data_validations.dataValidation),
            editable_cells=worksheet.editable_count(),
        )

    @staticmethod
    def _dimensions(openpyxl_ws: OpenpyxlWorksheet) -> tuple[int, int]:
        if not openpyxl_ws.dimensions or ":" not in openpyxl_ws.dimensions:
            return openpyxl_ws.max_row or 0, openpyxl_ws.max_column or 0
        end_cell = openpyxl_ws.dimensions.split(":", maxsplit=1)[1]
        row_match = re.search(r"\d+$", end_cell)
        col_match = re.search(r"^[A-Z]+", end_cell)
        row = int(row_match.group()) if row_match else 0
        col = WorkbookFingerprinter._col_letters_to_number(col_match.group()) if col_match else 0
        return row, col

    @staticmethod
    def _col_letters_to_number(letters: str) -> int:
        """Convert column letters to column number."""
        result = 0
        for char in letters:
            result = result * 26 + (ord(char) - ord("A") + 1)
        return result

    @staticmethod
    def _count_colors(worksheet: Worksheet) -> dict[str, int]:
        """Count occurrences of each color in a worksheet."""
        color_counts: dict[str, int] = {}
        for cell in worksheet.cells.values():
            if cell.fill:
                color = str(cell.fill).upper()
                if color and color != "NONE":
                    color_counts[color] = color_counts.get(color, 0) + 1
        return color_counts


def _keeps_vba(path: Path) -> bool:
    return path.suffix.lower() in {".xlsm", ".xltm"}
