# PDIE - ProAssist Document Intelligence Engine

A production-grade document intelligence engine for Excel workbooks, with support for analysis, comparison, templating, and filling.

## Overview

PDIE provides comprehensive analysis of Excel workbooks including:

- **Workbook Analysis**: Fingerprinting, structure analysis, editable field detection
- **Version Comparison**: Detect changes across workbook versions with confidence scoring
- **Smart Templates**: Package workbooks as reusable templates with metadata
- **Template Filling**: Populate templates from JSON data while preserving formulas and formatting
- **HTML Reports**: Interactive visual reports of workbook structure and changes

## Technology

- Python 3.12+
- openpyxl for Excel handling
- Pydantic v2 for serialization
- Typer for CLI
- Rich for terminal output
- pytest for testing

## Installation

```bash
cd PDIE
pip install -e .
```

### Windows setup.exe installer

PDIE includes an installer build script that produces a Windows installer at
`dist/installer/setup.exe`. Build it from a Windows machine with Inno Setup 6
and the installer build dependencies installed:

```powershell
cd C:\Users\BrianS\PDIE-main
.\installer\build_setup.bat
```

Or run the commands manually:

```powershell
cd C:\Users\BrianS\PDIE-main
py -m pip install -e ".[installer]"
py installer\build_setup.py
```

Do not compile `installer\pdie_setup.iss` directly until
`dist\pdie\pdie.exe` exists; the Inno Setup file wraps that built executable
into `setup.exe`. Use `py installer\build_setup.py --skip-installer` to build
only the standalone `dist/pdie/pdie.exe` CLI executable. If Inno Setup is not on
`PATH`, pass `--iscc-path C:\path\to\ISCC.exe`.

## Quick Start

```bash
# Analyze a workbook
pdie analyze workbook.xlsm

# Compare two workbook versions
pdie compare old.xlsm new.xlsm

# Package as template
pdie package workbook.xlsm

# Fill template with data
pdie fill template.template answers.json
```

## Project Structure

```
pdie/
├── cli.py              # CLI entry point
├── engine.py           # Main engine coordinator
├── core/               # Core data models
│   ├── workbook.py
│   ├── worksheet.py
│   ├── cell.py
│   └── fingerprint.py
├── readers/            # File readers
│   └── excel_reader.py
├── analyzers/          # Analysis engines
│   ├── workbook_analyzer.py
│   ├── worksheet_analyzer.py
│   ├── cell_analyzer.py
│   └── difference_engine.py
├── intelligence/       # Intelligent matching and detection
│   ├── worksheet_matcher.py
│   └── field_detector.py
├── metadata/           # Metadata generation
│   ├── generator.py
│   └── schema.py
├── package/            # Template packaging
│   ├── builder.py
│   ├── reader.py
│   └── manifest.py
├── reports/            # Report generation
│   ├── html_report.py
│   └── validation_report.py
└── utils/              # Utilities

tests/                 # Test suite
examples/              # Example workbooks and data
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
ruff format pdie tests
```

Lint:
```bash
ruff check pdie tests
```
