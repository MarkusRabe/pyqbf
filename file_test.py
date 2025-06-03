"""Tests for file reading and end-to-end functionality."""

import os

import parse
import lib


def test_read_satisfiable_tautology_file():
    """Test reading and parsing satisfiable tautology file."""
    file_path = "test_data/satisfiable_tautology.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(
        1, [[1], [-1]], [parse.QuantifierBlock([1], parse.QuantifierType.EXISTS)]
    )
    assert result == expected


def test_read_satisfiable_mixed_quantifiers_file():
    """Test reading and parsing satisfiable mixed quantifiers file."""
    file_path = "test_data/satisfiable_mixed_quantifiers.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(
        2,
        [[1, 2]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.EXISTS),
            parse.QuantifierBlock([2], parse.QuantifierType.FORALL),
        ],
    )
    assert result == expected


def test_read_classic_qbf_example_file():
    """Test reading and parsing classic QBF example file."""
    file_path = "test_data/classic_qbf_example.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(
        2,
        [[1, 2], [-1, 2]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2], parse.QuantifierType.EXISTS),
        ],
    )
    assert result == expected


def test_read_unsatisfiable_example_file():
    """Test reading and parsing unsatisfiable example file."""
    file_path = "test_data/unsatisfiable_example.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(
        2,
        [[1, 2], [-1, -2], [1, -2], [-1, 2]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2], parse.QuantifierType.EXISTS),
        ],
    )
    assert result == expected


def test_read_complex_alternating_file():
    """Test reading and parsing complex alternating quantifiers file."""
    file_path = "test_data/complex_alternating.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(
        4,
        [[1, 2, 3], [-1, -3, 4]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2], parse.QuantifierType.EXISTS),
            parse.QuantifierBlock([3], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([4], parse.QuantifierType.EXISTS),
        ],
    )
    assert result == expected


def test_read_large_formula_file():
    """Test reading and parsing large formula file."""
    file_path = "test_data/large_formula.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(
        5,
        [[1, 3], [2, 4], [-1, -2, 5], [3, -4, -5]],
        [
            parse.QuantifierBlock([1, 2], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([3, 4, 5], parse.QuantifierType.EXISTS),
        ],
    )
    assert result == expected


def test_solve_file_satisfiable_tautology():
    """Test solving satisfiable tautology file (currently returns UNSAT due to placeholder)."""
    file_path = "test_data/satisfiable_tautology.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior


def test_solve_file_satisfiable_mixed():
    """Test solving satisfiable mixed quantifiers file (currently returns UNSAT due to placeholder)."""
    file_path = "test_data/satisfiable_mixed_quantifiers.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior


def test_solve_file_unsatisfiable():
    """Test solving unsatisfiable file (currently returns UNSAT, which happens to be correct)."""
    file_path = "test_data/unsatisfiable_example.qdimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    assert result == "UNSAT"


def test_read_classical_sat_satisfiable_file():
    """Test reading and parsing classical SAT satisfiable file."""
    file_path = "test_data/classical_sat_satisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(1, [[1]], [])  # No quantifiers in classical SAT
    assert result == expected


def test_read_classical_sat_unsatisfiable_file():
    """Test reading and parsing classical SAT unsatisfiable file."""
    file_path = "test_data/classical_sat_unsatisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(1, [[1], [-1]], [])  # No quantifiers in classical SAT
    assert result == expected


def test_read_classical_sat_complex_file():
    """Test reading and parsing complex classical SAT file."""
    file_path = "test_data/classical_sat_complex.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = parse.from_qdimacs(content)
    expected = parse.QDimacs(
        2, [[1, 2], [-1, 2], [1, -2]], []  # No quantifiers in classical SAT
    )
    assert result == expected


def test_solve_classical_sat_satisfiable():
    """Test solving classical SAT satisfiable file (currently returns UNSAT due to placeholder)."""
    file_path = "test_data/classical_sat_satisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    # TODO: This should return "SAT" when a real solver is implemented
    assert result == "UNSAT"  # Current placeholder behavior


def test_solve_classical_sat_unsatisfiable():
    """Test solving classical SAT unsatisfiable file (currently returns UNSAT, which happens to be correct)."""
    file_path = "test_data/classical_sat_unsatisfiable.dimacs"
    assert os.path.exists(file_path), f"Test file {file_path} not found"

    with open(file_path, "r") as f:
        content = f.read()

    result = lib.solve_file(content)
    assert isinstance(result, str)
    assert result == "UNSAT"
