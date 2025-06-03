"""Tests for the formula module."""

import pytest

import formula
import parse


def test_literal_index():
    """Test that literal_index returns correct values for positive and negative literals."""
    positive_lit = formula.Literal(3, True)
    negative_lit = formula.Literal(3, False)

    assert positive_lit.literal_index() == 3
    assert negative_lit.literal_index() == -3


def test_literal_equality():
    """Test that literals are equal if they have the same variable and polarity."""
    lit1 = formula.Literal(3, True)
    lit2 = formula.Literal(3, True)
    lit3 = formula.Literal(3, False)

    assert lit1 == lit2
    assert lit1 != lit3
    assert lit2 != lit3

    assert hash(lit1) == hash(lit2)
    assert hash(lit1) != hash(lit3)
    assert hash(lit2) != hash(lit3)

    assert -lit1 == lit3
    assert -lit3 == lit1
    assert lit1 == -(-lit1)


def test_tautology():
    """Test that is_tautology returns True for clauses that are tautologies."""
    clause = formula.Clause.from_literals(
        [formula.Literal(1, True), formula.Literal(1, False)], index=0
    )

    assert clause.is_tautology()


def test_not_tautology():
    """Test that is_tautology returns False for clauses that are not tautologies."""
    clause = formula.Clause.from_literals(
        [formula.Literal(1, True), formula.Literal(2, True)], index=0
    )

    assert not clause.is_tautology()


def test_clause_from_qdimacs():
    """Test creating a clause from QDIMACS format."""
    phi = formula.Formula(parse.QDimacs(3, [[1, -2, 3]], []))
    clause = phi.clauses_by_index[0]

    assert len(clause.literals) == 3
    assert clause.index == 0


def test_formula_creation_simple():
    """Test creating a formula from a simple quantifier-free QDIMACS input."""
    qdimacs = parse.QDimacs(2, [[1, 2], [-1, -2]], [])
    formula_obj = formula.Formula(qdimacs)

    assert len(formula_obj.variables_by_index) == 2
    assert len(formula_obj.clauses) == 2


def test_resolve():
    """Test resolving two clauses."""
    phi = formula.Formula(parse.QDimacs(3, [], []))
    clause1 = phi.create_clause_from_qdimacs([1, 2, 3], 0)
    clause2 = phi.create_clause_from_qdimacs([-1, -2, -3], 1)
    phi.add_clause(clause1)
    phi.add_clause(clause2)

    variable_1 = filter(
        lambda v: v.index == 1, phi.variables_by_index.values()
    ).__next__()
    resolved_clause = phi.resolve(clause1, clause2, variable_1)

    assert len(resolved_clause.literals) == 4
    assert formula.Literal(2, True) in resolved_clause.literals
    assert formula.Literal(3, True) in resolved_clause.literals
    assert resolved_clause.is_tautology()


def test_eliminate_variable():
    """Test eliminating a variable from the formula."""
    qdimacs = parse.QDimacs(3, [[1, 2], [-1, -2], [1, 3]], [])
    phi = formula.Formula(qdimacs)
    variable_1 = filter(
        lambda v: v.index == 1, phi.variables_by_index.values()
    ).__next__()
    phi.eliminate_variable(variable_1)

    assert len(phi.variables_by_index) == 2
    assert len(phi.clauses) == 1
