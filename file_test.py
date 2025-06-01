"""Tests for file reading and end-to-end functionality."""

import os

from parse import QDimacs, QuantifierBlock
import lib


def test_read_satisfiable_tautology_file():
    """Test reading and parsing satisfiable tautology file."""
    file_path = "test_data/satisfiable_tautology.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = QDimacs.parse(content)
    expected = QDimacs(
        1,
        [[1], [-1]],
        [QuantifierBlock([1], "exists")]
    )
    assert result == expected


def test_read_satisfiable_mixed_quantifiers_file():
    """Test reading and parsing satisfiable mixed quantifiers file."""
    file_path = "test_data/satisfiable_mixed_quantifiers.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = QDimacs.parse(content)
    expected = QDimacs(
        2,
        [[1, 2]],
        [
            QuantifierBlock([1], "exists"),
            QuantifierBlock([2], "forall")
        ]
    )
    assert result == expected


def test_read_classic_qbf_example_file():
    """Test reading and parsing classic QBF example file."""
    file_path = "test_data/classic_qbf_example.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = QDimacs.parse(content)
    expected = QDimacs(
        2,
        [[1, 2], [-1, 2]],
        [
            QuantifierBlock([1], "forall"),
            QuantifierBlock([2], "exists")
        ]
    )
    assert result == expected


def test_read_unsatisfiable_example_file():
    """Test reading and parsing unsatisfiable example file."""
    file_path = "test_data/unsatisfiable_example.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = QDimacs.parse(content)
    expected = QDimacs(
        2,
        [[1, 2], [-1, -2], [1, -2], [-1, 2]],
        [
            QuantifierBlock([1], "forall"),
            QuantifierBlock([2], "exists")
        ]
    )
    assert result == expected


def test_read_complex_alternating_file():
    """Test reading and parsing complex alternating quantifiers file."""
    file_path = "test_data/complex_alternating.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = QDimacs.parse(content)
    expected = QDimacs(
        4,
        [[1, 2, 3], [-1, -3, 4]],
        [
            QuantifierBlock([1], "forall"),
            QuantifierBlock([2], "exists"),
            QuantifierBlock([3], "forall"),
            QuantifierBlock([4], "exists")
        ]
    )
    assert result == expected


def test_read_large_formula_file():
    """Test reading and parsing large formula file."""
    file_path = "test_data/large_formula.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = QDimacs.parse(content)
    expected = QDimacs(
        5,
        [[1, 3], [2, 4], [-1, -2, 5], [3, -4, -5]],
        [
            QuantifierBlock([1, 2], "forall"),
            QuantifierBlock([3, 4, 5], "exists")
        ]
    )
    assert result == expected


def test_solve_file_satisfiable_tautology():
    """Test solving satisfiable tautology file (currently returns UNSAT due to placeholder)."""
    file_path = "test_data/satisfiable_tautology.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = lib.solve_file(content)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior


def test_solve_file_satisfiable_mixed():
    """Test solving satisfiable mixed quantifiers file (currently returns UNSAT due to placeholder)."""
    file_path = "test_data/satisfiable_mixed_quantifiers.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    result = lib.solve_file(content)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior


def test_solve_file_unsatisfiable():
    """Test solving unsatisfiable file (currently returns UNSAT, which happens to be correct)."""
    file_path = "test_data/unsatisfiable_example.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, 'r') as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    assert result == "UNSAT"


def test_read_classical_sat_satisfiable_file():
    """Test reading and parsing classical SAT satisfiable file."""
    file_path = "test_data/classical_sat_satisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, 'r') as f:
        content = f.read()

    result = QDimacs.parse(content)
    expected = QDimacs(
        1,
        [[1]],
        []  # No quantifiers in classical SAT
    )
    assert result == expected


def test_read_classical_sat_unsatisfiable_file():
    """Test reading and parsing classical SAT unsatisfiable file."""
    file_path = "test_data/classical_sat_unsatisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, 'r') as f:
        content = f.read()

    result = QDimacs.parse(content)
    expected = QDimacs(
        1,
        [[1], [-1]],
        []  # No quantifiers in classical SAT
    )
    assert result == expected


def test_read_classical_sat_complex_file():
    """Test reading and parsing complex classical SAT file."""
    file_path = "test_data/classical_sat_complex.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, 'r') as f:
        content = f.read()

    result = QDimacs.parse(content)
    expected = QDimacs(
        2,
        [[1, 2], [-1, 2], [1, -2]],
        []  # No quantifiers in classical SAT
    )
    assert result == expected


def test_solve_classical_sat_satisfiable():
    """Test solving classical SAT satisfiable file (currently returns UNSAT due to placeholder)."""
    file_path = "test_data/classical_sat_satisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, 'r') as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior


def test_solve_classical_sat_unsatisfiable():
    """Test solving classical SAT unsatisfiable file (currently returns UNSAT, which happens to be correct)."""
    file_path = "test_data/classical_sat_unsatisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, 'r') as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    assert result == "UNSAT"
