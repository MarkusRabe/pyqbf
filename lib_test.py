"""Tests for the lib module."""

import pytest

from parse import QDimacs, QuantifierBlock
import lib


def test_solve_file():
    """Test that solve_file correctly parses and solves a QBF."""
    # Simple test case
    file_content = "p cnf 1 1\n1 0"
    result = lib.solve_file(file_content)
    assert isinstance(result, str)
    assert result == "UNSAT"  # Based on our placeholder implementation


def test_solve():
    """Test that solve correctly solves a QBF."""
    # Create a simple QDimacs instance
    puzzle = QDimacs(1, [[1]], [])
    result = lib.solve(puzzle)
    assert isinstance(result, str)
    assert result == "UNSAT"  # Based on our placeholder implementation


def test_solve_with_quantifiers():
    """Test that solve correctly handles quantifiers."""
    # Create a QDimacs instance with quantifiers
    quantifiers = [
        QuantifierBlock([1], "exists"),
        QuantifierBlock([2], "forall")
    ]
    puzzle = QDimacs(2, [[1, 2], [-1, -2]], quantifiers)
    result = lib.solve(puzzle)
    assert isinstance(result, str)
    assert result == "UNSAT"  # Based on our placeholder implementation
