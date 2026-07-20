"""Fingerprinting models for workbooks and worksheets."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WorkbookFingerprint:
    """Fingerprint of a workbook for identification and comparison."""

    workbook_name: str
    file_type: str
    worksheet_count: int
    contains_macros: bool = False
    contains_images: bool = False
    contains_tables: bool = False
    dropdown_count: int = 0
    formula_count: int = 0
    merged_range_count: int = 0
    named_range_count: int = 0
    protected: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class WorksheetFingerprint:
    """Fingerprint of a worksheet for identification and matching."""

    name: str
    rows: int
    columns: int
    merged_cells: int = 0
    formula_cells: int = 0
    tables: int = 0
    images: int = 0
    hidden: bool = False
    color_counts: dict[str, int] = field(default_factory=dict)
    named_regions: int = 0
    editable_cells: int = 0
    metadata: dict = field(default_factory=dict)
