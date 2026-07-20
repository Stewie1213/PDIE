"""Analyzer for workbooks."""

from pdie.analyzers.worksheet_analyzer import WorksheetAnalyzer
from pdie.core.workbook import Workbook


class WorkbookAnalyzer:
    """Analyzes workbooks and coordinates worksheet analysis."""

    @staticmethod
    def analyze_workbook(workbook: Workbook) -> None:
        """Analyze all worksheets in a workbook.

        Args:
            workbook: The workbook to analyze.
        """
        for worksheet in workbook.worksheets.values():
            WorksheetAnalyzer.analyze_worksheet(worksheet)

    @staticmethod
    def get_summary(workbook: Workbook) -> dict:
        """Get a summary of the workbook analysis.

        Args:
            workbook: The workbook to summarize.

        Returns:
            dict: Analysis summary.
        """
        summary = {
            "workbook_name": workbook.name,
            "worksheet_count": workbook.worksheet_count(),
            "total_cells": workbook.total_cells(),
            "total_formulas": workbook.total_formulas(),
            "total_editable": workbook.total_editable_cells(),
            "worksheets": {},
        }

        for ws_name, worksheet in workbook.worksheets.items():
            ws_summary = {
                "name": worksheet.name,
                "index": worksheet.index,
                "hidden": worksheet.hidden,
                "protected": worksheet.protected,
                "cell_count": worksheet.cell_count(),
                "formula_count": worksheet.formula_count(),
                "editable_count": worksheet.editable_count(),
                "field_type_counts": WorksheetAnalyzer.count_by_field_type(worksheet),
                "data_region": WorksheetAnalyzer.detect_data_region(worksheet),
                "header_row": WorksheetAnalyzer.detect_header_row(worksheet),
            }

            # Add fingerprint info if available
            if worksheet.fingerprint:
                ws_summary["fingerprint"] = {
                    "rows": worksheet.fingerprint.rows,
                    "columns": worksheet.fingerprint.columns,
                    "merged_cells": worksheet.fingerprint.merged_cells,
                    "formula_cells": worksheet.fingerprint.formula_cells,
                }

            summary["worksheets"][ws_name] = ws_summary

        # Add fingerprint info if available
        if workbook.fingerprint:
            summary["fingerprint"] = {
                "file_type": workbook.fingerprint.file_type,
                "contains_macros": workbook.fingerprint.contains_macros,
                "contains_images": workbook.fingerprint.contains_images,
                "contains_tables": workbook.fingerprint.contains_tables,
                "dropdown_count": workbook.fingerprint.dropdown_count,
                "merged_range_count": workbook.fingerprint.merged_range_count,
                "named_range_count": workbook.fingerprint.named_range_count,
                "protected": workbook.fingerprint.protected,
            }

        return summary
