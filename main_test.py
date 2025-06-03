"""Tests for the main module."""

import pytest
import sys
import io
import tempfile
import os

import main


def test_main_with_valid_file(monkeypatch):
    """Test that main correctly processes a valid file."""
    # Create a temporary file with valid content
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("p cnf 1 1\n1 0")
        temp_file_path = temp_file.name

    try:
        # Redirect stdout to capture output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Mock sys.argv
        monkeypatch.setattr(sys, "argv", ["main.py", temp_file_path])

        # Call main
        main.main()

        # Check output
        lines = captured_output.getvalue().split()
        assert "SAT" in lines
    finally:
        # Clean up
        sys.stdout = sys.__stdout__
        os.unlink(temp_file_path)


def test_main_with_nonexistent_file(monkeypatch, capsys):
    """Test that main correctly handles a nonexistent file."""
    # Mock sys.argv with a nonexistent file
    monkeypatch.setattr(sys, "argv", ["main.py", "nonexistent_file.txt"])

    # Mock sys.exit to prevent the test from exiting
    def mock_exit(code):
        raise SystemExit(code)

    monkeypatch.setattr(sys, "exit", mock_exit)

    # Call main and expect SystemExit
    with pytest.raises(SystemExit) as excinfo:
        main.main()

    # Check exit code
    assert excinfo.value.code == 1

    # Check error message
    captured = capsys.readouterr()
    assert "not found" in captured.err
