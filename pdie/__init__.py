"""PDIE - ProAssist Document Intelligence Engine."""

from typing import Any

from openpyxl.workbook.defined_name import DefinedName, DefinedNameDict

__version__ = "0.1.0"


if not hasattr(DefinedNameDict, "append"):

    def _append_defined_name(self: DefinedNameDict, value: DefinedName | dict[str, Any]) -> None:
        """Provide openpyxl 3.1-compatible append support for older call sites."""
        defined_name = value if isinstance(value, DefinedName) else DefinedName(**value)
        self.add(defined_name)

    DefinedNameDict.append = _append_defined_name  # type: ignore[attr-defined]
