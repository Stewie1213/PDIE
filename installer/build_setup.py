"""Build a Windows ``setup.exe`` installer for the PDIE CLI.

This helper creates a standalone ``pdie.exe`` with PyInstaller and then wraps it
in a Windows installer named ``setup.exe`` with Inno Setup.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = PROJECT_ROOT / "build" / "installer"
APP_DIST_DIR = PROJECT_ROOT / "dist" / "pdie"
INSTALLER_OUTPUT_DIR = PROJECT_ROOT / "dist" / "installer"
INNO_SCRIPT = PROJECT_ROOT / "installer" / "pdie_setup.iss"


def run(command: list[str], *, cwd: Path = PROJECT_ROOT) -> None:
    """Run a command and stream its output."""
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def find_iscc(explicit_path: str | None = None) -> str:
    """Return the Inno Setup compiler path, or raise a clear error."""
    candidates = [explicit_path] if explicit_path else []
    candidates.extend(
        [
            shutil.which("iscc"),
            shutil.which("ISCC.exe"),
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
        ]
    )

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)

    raise RuntimeError(
        "Inno Setup compiler (ISCC.exe) was not found. Install Inno Setup 6 "
        "or pass --iscc-path C:\\path\\to\\ISCC.exe."
    )


def build_executable() -> None:
    """Build the standalone PDIE command-line executable."""
    APP_DIST_DIR.mkdir(parents=True, exist_ok=True)
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--onefile",
            "--name",
            "pdie",
            "--distpath",
            str(APP_DIST_DIR),
            "--workpath",
            str(BUILD_DIR / "pyinstaller"),
            "pdie/cli.py",
        ]
    )


def build_installer(iscc_path: str | None = None) -> None:
    """Compile the Inno Setup script into dist/installer/setup.exe."""
    if platform.system() != "Windows":
        raise RuntimeError("setup.exe must be built on Windows with Inno Setup installed.")

    INSTALLER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run([find_iscc(iscc_path), str(INNO_SCRIPT)])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the PDIE Windows setup.exe installer.")
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Only build dist/pdie/pdie.exe; do not compile setup.exe with Inno Setup.",
    )
    parser.add_argument(
        "--iscc-path",
        help="Path to ISCC.exe if it is not available on PATH.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_executable()
    if not args.skip_installer:
        build_installer(args.iscc_path)
        print(f"Created installer: {INSTALLER_OUTPUT_DIR / 'setup.exe'}")


if __name__ == "__main__":
    main()
