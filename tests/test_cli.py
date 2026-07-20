"""Tests for the CLI."""

from pathlib import Path

from typer.testing import CliRunner

from pdie.cli import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_analyze_command_help(self) -> None:
        """Test analyze command help."""
        result = runner.invoke(app, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze a workbook" in result.stdout

    def test_compare_command_help(self) -> None:
        """Test compare command help."""
        result = runner.invoke(app, ["compare", "--help"])
        assert result.exit_code == 0
        assert "Compare two workbook" in result.stdout

    def test_package_command_help(self) -> None:
        """Test package command help."""
        result = runner.invoke(app, ["package", "--help"])
        assert result.exit_code == 0
        assert "Smart Template" in result.stdout

    def test_fill_command_help(self) -> None:
        """Test fill command help."""
        result = runner.invoke(app, ["fill", "--help"])
        assert result.exit_code == 0
        assert "Fill a Smart Template" in result.stdout

    def test_validate_command_help(self) -> None:
        """Test validate command help."""
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate a Smart Template" in result.stdout

    def test_analyze_nonexistent_file(self) -> None:
        """Test analyze with non-existent file."""
        result = runner.invoke(app, ["analyze", "/nonexistent/file.xlsx"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_analyze_valid_workbook(self, sample_workbook: Path) -> None:
        """Test analyze with valid workbook."""
        result = runner.invoke(app, ["analyze", str(sample_workbook)])
        assert result.exit_code == 0
        assert "Analyzing" in result.stdout
        assert "✓" in result.stdout
