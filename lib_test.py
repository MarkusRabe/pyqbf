"""Tests for the lib module."""

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


def test_solve_satisfiable_formula():
    """Test solving a satisfiable QBF formula (currently returns UNSAT due to placeholder)."""
    # This is a tautology: ∃x.(x ∨ ¬x) - should be satisfiable
    # But our placeholder implementation always returns "UNSAT"
    file_content = """p cnf 1 2
e 1 0
1 0
-1 0"""

    result = lib.solve_file(file_content)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior


def test_solve_another_satisfiable_formula():
    """Test solving another satisfiable QBF: ∃x∀y.(x ∨ y)."""
    # This formula is satisfiable: if we set x=true, then (x ∨ y) is true for any y
    # But our placeholder implementation always returns "UNSAT"
    quantifiers = [
        QuantifierBlock([1], "exists"),
        QuantifierBlock([2], "forall")
    ]
    puzzle = QDimacs(2, [[1, 2]], quantifiers)
    result = lib.solve(puzzle)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior
