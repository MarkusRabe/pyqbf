"""Tests for the parse module."""

import pytest

import parse


def test_parse_empty():
    """Test that parse.QDimacs.parse raises the correct exceptions."""
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("")
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("c")


def test_parse_header_raises():
    """Test that parse.QDimacs.parse raises the correct exceptions."""
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p")
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf")
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 0")
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1")
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("q cnf 1 1")  # Invalid header prefix
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p sat 1 1")  # Invalid format
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf a 1")  # Invalid number of variables
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 a")  # Invalid number of clauses
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 0 1")  # Invalid number of variables
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 -1")  # Invalid number of clauses


def test_parse_header():
    """Test parsing valid headers."""
    assert parse.QDimacs.parse("p cnf 1 0") == parse.QDimacs(1, [], [])


def test_parse_comments():
    """Test that parse.QDimacs.parse ignores comments."""
    assert parse.QDimacs.parse("c\np cnf 1 0") == parse.QDimacs(1, [], [])
    assert parse.QDimacs.parse("c\np cnf 1 0\nc") == parse.QDimacs(1, [], [])


def test_parse_clauses():
    """Test parsing valid clauses."""
    assert parse.QDimacs.parse("p cnf 1 1\n1 0") == parse.QDimacs(1, [[1]], [])
    assert parse.QDimacs.parse("p cnf 1 2\n1 0\n-1 0") == parse.QDimacs(1, [[1], [-1]], [])
    assert parse.QDimacs.parse("p cnf 2 2\n1 2 0\n-1 0") == parse.QDimacs(2, [[1, 2], [-1]], [])


def test_parse_invalid_clauses():
    """Test parsing invalid clauses."""
    # Clause without ending 0
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\n1")

    # Clause with invalid literal
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\nabc 0")

    # Empty clause
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\n0")

    # Clause with 0 in the middle
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\n1 0 2 0")

    # Clause with variable out of range
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\n2 0")

    # Duplicate clause
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 2\n1 0\n1 0")

    # Test that empty clauses are rejected
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\n 0")

    # Test that clauses with 0 in them are rejected
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\n0 1 0")


def test_parse_qdimacs():
    """Test that parse_qdimacs correctly parses a QDIMACS file."""
    # Test that parse_qdimacs calls parse.QDimacs.parse
    assert parse.parse_qdimacs("p cnf 1 1\n1 0") == parse.QDimacs(1, [[1]], [])


def test_parse_forall_quantifier():
    """Test parsing forall quantifier."""
    result = parse.QDimacs.parse("p cnf 2 1\na 1 2 0\n1 2 0")
    expected = parse.QDimacs(2, [[1, 2]], [parse.QuantifierBlock([1, 2], parse.QuantifierType.FORALL)])
    assert result == expected


def test_parse_exists_quantifier():
    """Test parsing exists quantifier."""
    result = parse.QDimacs.parse("p cnf 2 1\ne 1 2 0\n1 2 0")
    expected = parse.QDimacs(2, [[1, 2]], [parse.QuantifierBlock([1, 2], parse.QuantifierType.EXISTS)])
    assert result == expected


def test_parse_multiple_quantifier_blocks():
    """Test parsing multiple quantifier blocks."""
    result = parse.QDimacs.parse("p cnf 4 1\na 1 2 0\ne 3 4 0\n1 2 3 4 0")
    expected = parse.QDimacs(
        4,
        [[1, 2, 3, 4]],
        [
            parse.QuantifierBlock([1, 2], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([3, 4], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_invalid_quantifier_variable():
    """Test parsing quantifier with invalid variable name."""
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 2 1\na abc 0\n1 2 0")


def test_empty_quantifier_block():
    """Test parsing empty quantifier block."""
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\na 0\n1 0")


def test_quantifier_block_whitespace_only():
    """Test parsing quantifier block with only whitespace."""
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\na \n1 0")


def test_quantifier_block_missing_terminator():
    """Test parsing quantifier block without 0 terminator."""
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 2 1\na 1 2\n1 2 0")


def test_quantifier_block_no_variables():
    """Test parsing quantifier block with no variables at all."""
    with pytest.raises(parse.QDimacsParseError):
        parse.QDimacs.parse("p cnf 1 1\na\n1 0")


def test_quantifier_block_methods():
    """Test the QuantifierBlock methods."""
    forall_block = parse.QuantifierBlock([1, 2], parse.QuantifierType.FORALL)
    exists_block = parse.QuantifierBlock([3, 4], parse.QuantifierType.EXISTS)

    assert forall_block.is_forall() is True
    assert forall_block.is_exists() is False

    assert exists_block.is_forall() is False
    assert exists_block.is_exists() is True


def test_tautology():
    """Test parsing a tautology: ∃x.(x ∨ ¬x)."""
    qdimacs = """p cnf 1 2
e 1 0
1 -1 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        1,
        [[1, -1]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_qdimacs_str():
    """Test the parse.QDimacs.__str__ method."""
    qdimacs = parse.QDimacs(2, [[1, 2], [-1, -2]], [])
    expected = "p cnf 2 2\n1 2 0\n-1 -2 0"
    assert str(qdimacs) == expected


def test_classic_qbf_example():
    """Test parsing classic QBF example: ∀x.∃y. (x ∨ y) ∧ (¬x ∨ y)."""
    # This is a classic example from multiple QBF papers
    qdimacs = """p cnf 2 2
a 1 0
e 2 0
1 2 0
-1 2 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        2,
        [[1, 2], [-1, 2]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_simple_qbf_example():
    """Test parsing simple QBF example: ∀x∃y.(x ∨ ¬y)."""
    qdimacs = """p cnf 2 1
a 1 0
e 2 0
1 -2 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        2,
        [[1, -2]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_multi_variable_exists_block():
    """Test parsing QBF with multiple variables in exists block: ∀1∃2∃3 : (1∨2)∧(¬1∨¬2∨3)."""
    qdimacs = """p cnf 3 2
a 1 0
e 2 3 0
1 2 0
-1 -2 3 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        3,
        [[1, 2], [-1, -2, 3]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2, 3], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_alternating_quantifiers():
    """Test alternating quantifier pattern: ∀1∃2∀3∃4."""
    qdimacs = """p cnf 4 2
a 1 0
e 2 0
a 3 0
e 4 0
1 2 3 0
-1 -3 4 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        4,
        [[1, 2, 3], [-1, -3, 4]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2], parse.QuantifierType.EXISTS),
            parse.QuantifierBlock([3], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([4], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_multiple_variables_per_quantifier_block():
    """Test quantifier blocks with multiple variables each."""
    qdimacs = """p cnf 6 3
a 1 2 3 0
e 4 5 6 0
1 4 0
2 5 0
3 6 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        6,
        [[1, 4], [2, 5], [3, 6]],
        [
            parse.QuantifierBlock([1, 2, 3], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([4, 5, 6], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_larger_formula_with_comments():
    """Test parsing larger QDIMACS formula with 5 variables and comments."""
    qdimacs = """c This is a comment
c Another comment line
p cnf 5 4
a 1 2 0
e 3 4 5 0
1 3 0
2 4 0
-1 -2 5 0
3 -4 -5 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        5,
        [[1, 3], [2, 4], [-1, -2, 5], [3, -4, -5]],
        [
            parse.QuantifierBlock([1, 2], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([3, 4, 5], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_interspersed_comments():
    """Test parsing QDIMACS with comments interspersed between quantifiers and clauses."""
    qdimacs = """c QBF example from research
c Formula: ∀x∃y.(x ∨ y) ∧ (¬x ∨ y)
p cnf 2 2
c Quantifier block for x
a 1 0
c Quantifier block for y
e 2 0
c First clause: x ∨ y
1 2 0
c Second clause: ¬x ∨ y
-1 2 0
c End of formula"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        2,
        [[1, 2], [-1, 2]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.FORALL),
            parse.QuantifierBlock([2], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_classical_sat_formula():
    """Test parsing a classical SAT formula (DIMACS without quantifiers)."""
    # This is a simple satisfiable SAT formula: just x
    # Classical DIMACS files don't have quantifier blocks
    qdimacs = """p cnf 1 1
1 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        1,
        [[1]],
        []  # No quantifiers in classical SAT
    )
    assert result == expected


def test_classical_sat_unsatisfiable():
    """Test parsing an unsatisfiable classical SAT formula."""
    # This is unsatisfiable: x AND NOT x
    qdimacs = """p cnf 1 2
1 0
-1 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        1,
        [[1], [-1]],
        []  # No quantifiers in classical SAT
    )
    assert result == expected


def test_classical_sat_multiple_variables():
    """Test parsing classical SAT formula with multiple variables."""
    # (x1 OR x2) AND (NOT x1 OR x2) - satisfiable by setting x2=true
    qdimacs = """p cnf 2 2
1 2 0
-1 2 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        2,
        [[1, 2], [-1, 2]],
        []  # No quantifiers in classical SAT
    )
    assert result == expected


def test_satisfiable_qbf_formula():
    """Test parsing a satisfiable QBF formula: ∃x.(x ∨ ¬x)."""
    # This is a simple tautology that should be satisfiable
    # ∃x.(x ∨ ¬x) is always true regardless of x's value
    qdimacs = """p cnf 1 2
e 1 0
1 0
-1 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        1,
        [[1], [-1]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.EXISTS)
        ]
    )
    assert result == expected


def test_another_satisfiable_qbf():
    """Test parsing another satisfiable QBF: ∃x∀y.(x ∨ y)."""
    # This formula is satisfiable: if we set x=true, then (x ∨ y) is true for any y
    qdimacs = """p cnf 2 1
e 1 0
a 2 0
1 2 0"""

    result = parse.QDimacs.parse(qdimacs)
    expected = parse.QDimacs(
        2,
        [[1, 2]],
        [
            parse.QuantifierBlock([1], parse.QuantifierType.EXISTS),
            parse.QuantifierBlock([2], parse.QuantifierType.FORALL)
        ]
    )
    assert result == expected
