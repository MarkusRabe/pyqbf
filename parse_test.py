"""Tests for the parse module."""

import pytest

from parse import QDimacs, QDimacsParseError, QuantifierBlock, parse_qdimacs


def test_parse_empty():
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("")
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("c")


def test_parse_header_raises():
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p")
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf")
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 0")
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1")
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("q cnf 1 1")  # Invalid header prefix
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p sat 1 1")  # Invalid format
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf a 1")  # Invalid number of variables
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 a")  # Invalid number of clauses
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 0 1")  # Invalid number of variables
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 -1")  # Invalid number of clauses


def test_parse_header():
    assert QDimacs.parse("p cnf 1 0") == QDimacs(1, [], [])


def test_parse_clauses():
    assert QDimacs.parse("p cnf 1 1\n1 0") == QDimacs(1, [[1]], [])
    assert QDimacs.parse("p cnf 1 2\n1 0\n-1 0") == QDimacs(1, [[1], [-1]], [])
    assert QDimacs.parse("p cnf 2 2\n1 2 0\n-1 0") == QDimacs(2, [[1, 2], [-1]], [])


def test_parse_invalid_clauses():
    """Test parsing invalid clauses."""
    # Clause without ending 0
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 1\n1")

    # Clause with invalid literal
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 1\nabc 0")

    # Empty clause
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 1\n0")

    # Clause with 0 in the middle
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 1\n1 0 2 0")

    # Clause with variable out of range
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 1\n2 0")

    # Duplicate clause
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 2\n1 0\n1 0")

    # Test that empty clauses are rejected
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 1\n 0")

    # Test that clauses with 0 in them are rejected
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 1 1\n0 1 0")


def test_parse_qdimacs():
    """Test that parse_qdimacs correctly parses a QDIMACS file."""
    # Test that parse_qdimacs calls QDimacs.parse
    assert parse_qdimacs("p cnf 1 1\n1 0") == QDimacs(1, [[1]], [])


def test_parse_quantifiers():
    """Test parsing quantifiers."""
    # Test forall quantifier
    result = QDimacs.parse("p cnf 2 1\na 1 2\n1 2 0")
    expected = QDimacs(2, [[1, 2]], [QuantifierBlock([1, 2], "forall")])
    assert result == expected

    # Test exists quantifier
    result = QDimacs.parse("p cnf 2 1\ne 1 2\n1 2 0")
    expected = QDimacs(2, [[1, 2]], [QuantifierBlock([1, 2], "exists")])
    assert result == expected

    # Test multiple quantifiers
    result = QDimacs.parse("p cnf 4 1\na 1 2\ne 3 4\n1 2 3 4 0")
    expected = QDimacs(
        4,
        [[1, 2, 3, 4]],
        [
            QuantifierBlock([1, 2], "forall"),
            QuantifierBlock([3, 4], "exists")
        ]
    )
    assert result == expected


def test_parse_invalid_quantifiers():
    """Test parsing invalid quantifiers."""
    # Invalid quantifier variable
    with pytest.raises(QDimacsParseError):
        QDimacs.parse("p cnf 2 1\na abc\n1 2 0")


def test_quantifier_block_methods():
    """Test the QuantifierBlock methods."""
    forall_block = QuantifierBlock([1, 2], "forall")
    exists_block = QuantifierBlock([3, 4], "exists")

    assert forall_block.is_forall() is True
    assert forall_block.is_exists() is False

    assert exists_block.is_forall() is False
    assert exists_block.is_exists() is True


def test_qdimacs_str():
    """Test the QDimacs.__str__ method."""
    qdimacs = QDimacs(2, [[1, 2], [-1, -2]], [])
    expected = "p cnf 2 2\n1 2 0\n-1 -2 0"
    assert str(qdimacs) == expected
