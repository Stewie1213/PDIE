"""Interactive HTML workbook analysis reports."""

from dataclasses import asdict, is_dataclass
from html import escape
from pathlib import Path
from typing import Any

from jinja2 import Template

from pdie.core.cell import Cell
from pdie.core.workbook import Workbook
from pdie.core.worksheet import Worksheet


class HtmlReport:
    """Generates self-contained HTML reports for analyzed workbooks."""

    def generate(self, workbook: Workbook, output_path: Path | None = None) -> Path:
        """Generate an HTML report and return its path."""
        if output_path is None:
            output_path = self._default_output_path(workbook)
        html = Template(_REPORT_TEMPLATE).render(
            workbook=workbook,
            workbook_fingerprint=self._to_dict(workbook.fingerprint),
            worksheets=list(workbook.worksheets.values()),
            cell_classes=self._cell_classes,
            cell_metadata=self._cell_metadata,
        )
        output_path.write_text(html, encoding="utf-8")
        return output_path

    @staticmethod
    def _default_output_path(workbook: Workbook) -> Path:
        base_dir = workbook.file_path.parent if workbook.file_path else Path.cwd()
        return base_dir / f"{workbook.name}.html"

    @staticmethod
    def _to_dict(value: object) -> dict[str, Any]:
        if value is None:
            return {}
        if is_dataclass(value):
            return asdict(value)
        return dict(value) if isinstance(value, dict) else {}

    @staticmethod
    def _cell_classes(cell: Cell) -> str:
        classes = ["cell"]
        if cell.is_editable():
            classes.append("editable")
        if cell.locked:
            classes.append("protected")
        if cell.is_formula():
            classes.append("formula")
        if cell.has_validation():
            classes.append("dropdown")
        if cell.merged:
            classes.append("merged")
        if cell.hidden:
            classes.append("hidden")
        return " ".join(classes)

    @staticmethod
    def _cell_metadata(cell: Cell, worksheet: Worksheet) -> str:
        parts = {
            "Sheet": worksheet.name,
            "Address": cell.address,
            "Value": cell.get_display_value(),
            "Formula": cell.formula or "",
            "Data Type": cell.data_type or "",
            "Editable Score": f"{cell.editable_score:.2f}",
            "Validation": cell.validation or "",
            "Number Format": cell.number_format or "",
            "Comment": cell.comment or "",
        }
        return escape("\n".join(f"{key}: {value}" for key, value in parts.items() if value != ""))


_REPORT_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ workbook.name|e }} Analysis</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; color: #1f2937; }
    .summary, .legend, .sheet { border: 1px solid #d1d5db; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
    .grid { border-collapse: collapse; font-size: 12px; }
    .grid th, .grid td { border: 1px solid #d1d5db; min-width: 70px; padding: 4px; }
    .row-header { background: #f3f4f6; position: sticky; left: 0; }
    .cell { cursor: pointer; background: #fff; }
    .editable { background: #dcfce7; }
    .protected { outline: 2px solid #bfdbfe; outline-offset: -2px; }
    .formula { background: #fef3c7; }
    .dropdown { border-bottom: 3px solid #8b5cf6 !important; }
    .merged { box-shadow: inset 0 0 0 2px #f97316; }
    .hidden { opacity: 0.45; }
    #details { white-space: pre-wrap; background: #111827; color: #f9fafb; padding: 1rem; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>{{ workbook.name|e }} Workbook Analysis</h1>
  <section class="summary">
    <h2>Workbook Overview</h2>
    <p>Worksheets: {{ workbook.worksheet_count() }} | Cells: {{ workbook.total_cells() }} | Formulas: {{ workbook.total_formulas() }} | Editable: {{ workbook.total_editable_cells() }}</p>
    <ul>{% for key, value in workbook_fingerprint.items() %}<li><strong>{{ key|replace('_', ' ')|title }}:</strong> {{ value }}</li>{% endfor %}</ul>
  </section>
  <section class="legend"><strong>Legend:</strong> editable, protected, formula, dropdown, merged, hidden cells are highlighted. Click any cell for metadata.</section>
  <section><h2>Cell Metadata</h2><div id="details">Click a cell to inspect metadata.</div></section>
  {% for sheet in worksheets %}
  <section class="sheet">
    <h2>{{ sheet.name|e }}</h2>
    <p>Cells: {{ sheet.cell_count() }} | Formulas: {{ sheet.formula_count() }} | Editable: {{ sheet.editable_count() }} | Hidden: {{ sheet.hidden }} | Protected: {{ sheet.protected }}</p>
    <table class="grid">
      {% for row_number in range(1, (sheet.fingerprint.rows if sheet.fingerprint else 20) + 1) %}
      <tr><th class="row-header">{{ row_number }}</th>
        {% for cell in sheet.get_row(row_number) %}
        <td class="{{ cell_classes(cell) }}" onclick="showDetails(this)" data-details="{{ cell_metadata(cell, sheet) }}">{{ cell.get_display_value()|e }}</td>
        {% endfor %}
      </tr>
      {% endfor %}
    </table>
  </section>
  {% endfor %}
<script>function showDetails(el){document.getElementById('details').textContent=el.dataset.details;}</script>
</body>
</html>
"""
