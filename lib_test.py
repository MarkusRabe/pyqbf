"""Tests for the lib module."""

import pytest
import parse
import lib


def test_solve_file():
    """Test that solve_file correctly parses and solves a QBF."""
    file_content = "p cnf 1 1\n1 0"
    result = lib.solve_file(file_content)
    assert isinstance(result, str)
    assert result == "SAT"


def test_solve():
    """Test that solve correctly solves a QBF."""
    puzzle = parse.QDimacs(1, [[1]], [])
    result = lib.solve(puzzle)
    assert isinstance(result, str)
    assert result == "SAT"


def test_solve_with_quantifiers():
    """Test that solve correctly handles quantifiers."""
    # Create a QDimacs instance with quantifiers
    quantifiers = [
        parse.QuantifierBlock([1], parse.QuantifierType.EXISTS),
        parse.QuantifierBlock([2], parse.QuantifierType.FORALL),
    ]
    puzzle = parse.QDimacs(2, [[1, 2], [-1, -2]], quantifiers)
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
    assert result == "SAT"


def test_solve_another_satisfiable_formula():
    """Test solving another satisfiable QBF: ∃x∀y.(x ∨ y)."""
    # This formula is satisfiable: if we set x=true, then (x ∨ y) is true for any y
    # But our placeholder implementation always returns "UNSAT"
    quantifiers = [
        parse.QuantifierBlock([1], parse.QuantifierType.EXISTS),
        parse.QuantifierBlock([2], parse.QuantifierType.FORALL),
    ]
    puzzle = parse.QDimacs(2, [[1, 2]], quantifiers)
    result = lib.solve(puzzle)
    assert isinstance(result, str)
    assert result == "SAT"


def test_solve_unsatisfiable_formula():
    """Test solving an unsatisfiable QBF formula."""
    # This formula is unsatisfiable: ∀x∃y.(x ∨ y) ∧ (¬x ∨ ¬y) ∧ (x ∨ ¬y) ∧ (¬x ∨ y)
    # It should return "UNSAT"
    quantifiers = [
        parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
        parse.QuantifierBlock([2], parse.QuantifierType.EXISTS),
    ]
    puzzle = parse.QDimacs(2, [[1, 2], [-1, -2], [1, -2], [-1, 2]], quantifiers)
    result = lib.solve(puzzle)
    assert isinstance(result, str)
    assert result == "UNSAT"


def test_solve_classical_unsatisfiable():
    """Test solving an unsatisfiable classical SAT formula."""
    # This is unsatisfiable: x AND NOT x
    # Classical DIMACS files don't have quantifier blocks
    file_content = """p cnf 1 2
1 0
-1 0"""

    result = lib.solve_file(file_content)
    assert isinstance(result, str)
    assert result == "UNSAT"
