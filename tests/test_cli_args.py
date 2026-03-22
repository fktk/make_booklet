import pytest
import subprocess
import sys

def test_cli_help_includes_a4_options():
    """Verify that --help shows the new A4 options."""
    result = subprocess.run([sys.executable, "-m", "make_booklet.cli", "--help"], 
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "--a4-orientation" in result.stdout
    assert "--a4-align" in result.stdout

def test_cli_accepts_a4_options(tmp_path):
    """Verify that CLI accepts new A4 options (even if they might fail execution due to missing file)."""
    # Just check if it doesn't fail with "unrecognized arguments"
    # We use a non-existent input file but that should fail AFTER argument parsing
    result = subprocess.run([sys.executable, "-m", "make_booklet.cli", 
                             "--to-a4", "--a4-orientation", "landscape", "--a4-align", "left",
                             "non_existent.pdf", "output.pdf"], 
                            capture_output=True, text=True)
    # It should fail with "Failed to open input PDF" or similar, NOT unrecognized arguments
    assert "unrecognized arguments" not in result.stderr
