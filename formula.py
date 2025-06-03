"""Data structures for QBF formulas."""

from typing import List, Dict, Set, Sequence, FrozenSet
from dataclasses import dataclass, field
import itertools
import functools
import parse

VariableIndex = int
ClauseIndex = int

QuantifierType = parse.QuantifierType


@dataclass(frozen=True)
class Literal:
    """Represents a literal in a QBF formula."""

    variable: VariableIndex
    is_positive: bool
    occurrences: Set["Clause"] = field(
        default_factory=set
    )  # notably, occurence set is not frozen

    def __post_init__(self):
        """Initialize the occurrences set."""

    def literal_index(self) -> int:
        """Return the index of this literal in the formula."""
        return self.variable if self.is_positive else -self.variable

    def __eq__(self, value):
        """Return whether this literal is equal to another."""
        if not isinstance(value, Literal):
            return False
        return self.variable == value.variable and self.is_positive == value.is_positive

    def __hash__(self):
        """Return the hash of this literal."""
        return hash((self.variable, self.is_positive))

    # TODO(markus): is this a good idea? Will lead to duplicate literal objects.
    def __neg__(self):
        """Return the negation of this literal."""
        return Literal(self.variable, not self.is_positive)


@dataclass(frozen=True)
class Variable:
    """Represents a variable in a QBF formula."""

    index: VariableIndex
    quantifier: QuantifierType
    positive: Literal = field(init=False)
    negative: Literal = field(init=False)

    def __post_init__(self):
        """Initialize the positive and negative literals."""
        object.__setattr__(self, "positive", Literal(self.index, True))
        object.__setattr__(self, "negative", Literal(self.index, False))

    def get_literal(self, is_positive: bool) -> Literal:
        """Return the positive or negative literal for this variable."""
        return self.positive if is_positive else self.negative

    def __hash__(self):
        """Return the hash of this variable."""
        return hash(self.index)

    def __eq__(self, value):
        """Return whether this variable is equal to another."""
        if not isinstance(value, Variable):
            return False
        return self.index == value.index


# Try to not create clauses other than through the Formula class.
@dataclass(frozen=True)  # frozen to allow it to be used in a set
class Clause:
    """Represents a clause in a QBF formula."""

    literals: FrozenSet[Literal]
    index: ClauseIndex | None = None
    is_original: bool = False

    @staticmethod
    def from_literals(
        literals: Sequence[Literal], index: ClauseIndex, is_original: bool = False
    ) -> "Clause":
        """Create a clause from a list of literals."""
        return Clause(frozenset(literals), index, is_original)

    def __hash__(self):
        """Return the hash of this clause."""
        return hash(frozenset(l.literal_index() for l in self.literals))

    def __eq__(self, other):
        """Return whether this clause is equal to another."""
        if not isinstance(other, Clause):
            return False
        return self.literals == other.literals

    def __repr__(self):
        """Return a string representation of this clause."""
        return f"Clause({self.literals})"

    def to_qdimacs(self) -> str:
        """Return a string representation of this clause in QDIMACS format."""
        clause_str = " ".join(str(l.literal_index()) for l in self.literals) + " 0"
        comment = (
            f"c Clause {self.index}, {'original' if self.is_original else 'derived'}"
        )
        return f"{comment}\n{clause_str}"

    def is_tautology(self) -> bool:
        """Return whether this clause is a tautology."""
        return any(-l in self.literals for l in self.literals)


class Formula:
    """Working representation of a QBF formula.

    Represents a QBF formula as a graph of variables and clauses."""

    def __init__(self, qdimacs: parse.QDimacs):
        self.quantifiers: List[parse.QuantifierBlock] = qdimacs.quantifiers
        if len(qdimacs.quantifiers) != 0:
            raise NotImplementedError("Only quantifier-free formulas are supported.")
        self.variables: Dict[VariableIndex, Variable] = {}
        self.clauses: Set[Clause] = set()
        self.clauses_by_index: Dict[ClauseIndex, Clause] = {}

        # Largest variable/clause index that MAY be in use.
        # 0 is not a valid variable index.
        self._largest_used_variable_index = 1
        self._largest_used_clause_index = 0

        for quantifier in qdimacs.quantifiers:
            for variable in quantifier.bound_variables:
                self.create_fresh_variable(variable, quantifier.quantifier_type)

        for variable_index in range(1, qdimacs.num_vars + 1):
            if variable_index not in self.variables:
                self.create_fresh_variable(variable_index)

        for index, clause in enumerate(qdimacs.clauses):
            for l in clause:
                var_index = abs(l)
                if var_index not in self.variables:
                    self.create_fresh_variable(var_index)
            clause = self.create_clause_from_qdimacs(clause, index)
            self.add_clause(clause)

    def next_fresh_variable_index(self) -> int:
        """Return the next fresh variable index."""
        while self._largest_used_variable_index in self.variables:
            self._largest_used_variable_index += 1
        return self._largest_used_variable_index

    def create_fresh_variable(
        self,
        index: int | None = None,
        quantifier: QuantifierType = QuantifierType.EXISTS,
    ) -> Variable:
        """Create a new variable with the given quantifier."""
        index = index or self.next_fresh_variable_index()
        assert index not in self.variables
        self.variables[index] = Variable(index, quantifier)
        return self.variables[index]

    def next_fresh_clause_index(self) -> int:
        """Return the next fresh clause index."""
        while self._largest_used_clause_index in self.clauses_by_index:
            self._largest_used_clause_index += 1
        return self._largest_used_clause_index

    def get_literal_by_index(self, literal_index: int) -> Literal:
        """Return the literal with the given QDIMACS index."""
        variable_index = abs(literal_index)
        is_positive = literal_index > 0
        return self.variables[variable_index].get_literal(is_positive)

    def create_clause_from_qdimacs(
        self, clause: Sequence[int], index: ClauseIndex
    ) -> Clause:
        """Create a clause from a list of QDIMACS literals."""
        literals = (self.get_literal_by_index(lit) for lit in clause)
        return Clause(frozenset(literals), index, is_original=True)

    def is_clause_subsumed(self, clause: Clause) -> bool:
        """Return whether the given clause is subsumed by another clause."""
        if clause in self.clauses:
            return True
        if clause.is_tautology():
            return True
        if not clause.literals:
            return False
        # Optimization: find literal with smallest number of occurrences
        rarest_literal = min(clause.literals, key=lambda l: len(l.occurrences))
        # Optimization: only check clauses that are shorter
        candidate_clauses = (
            c
            for c in rarest_literal.occurrences
            if len(c.literals) <= len(clause.literals)
        )
        return any(
            other.literals.issubset(clause.literals) for other in candidate_clauses
        )

    def add_clause(self, clause: Clause):
        """Add a clause to the formula."""
        assert (
            clause.index not in self.clauses
        ), f"Clause {clause.index} already in formula. {clause}, {self.clauses[clause.index]}"
        if not self.is_clause_subsumed(clause):
            self.clauses.add(clause)
            self.clauses_by_index[clause.index] = clause
            for literal in clause.literals:
                literal.occurrences.add(clause)
                assert literal is self.variables[literal.variable].get_literal(
                    literal.is_positive
                )

    def contains_empty_clause(self) -> bool:
        """Return whether this formula contains the empty clause."""
        return self.generate_empty_clause() in self.clauses

    def resolve(self, clause1: Clause, clause2: Clause, variable: Variable) -> Clause:
        """Resolve two clauses with respect to a variable."""
        assert variable.index in self.variables
        assert clause1 is self.clauses_by_index[clause1.index]
        assert clause2 is self.clauses_by_index[clause2.index]
        both_literals = itertools.chain(clause1.literals, clause2.literals)
        literals = (l for l in both_literals if l.variable != variable.index)
        return Clause.from_literals(
            literals, self.next_fresh_clause_index(), is_original=False
        )

    def to_qdimacs(self) -> str:
        """Return a string representation of this formula in QDIMACS format."""
        clauses_in_order = sorted(self.clauses, key=lambda c: c.index)
        clause_strings = (clause.to_qdimacs() for clause in clauses_in_order)
        header = f"p cnf {len(self.variables)} {len(self.clauses)}"
        all_lines = itertools.chain([header], clause_strings)
        return "\n".join(all_lines)

    @functools.lru_cache()
    def generate_empty_clause(self) -> Clause:
        """Generate an empty clause."""
        return Clause.from_literals(
            (), self.next_fresh_clause_index(), is_original=False
        )

    def eliminate_variable(self, variable: Variable) -> None:
        """Eliminate a variable from the formula."""
        assert variable.index in self.variables

        # Resolve all positive and negative literals
        for positive_clause in variable.positive.occurrences:
            for negative_clause in variable.negative.occurrences:
                resolvent = self.resolve(positive_clause, negative_clause, variable)
                if not resolvent.is_tautology():
                    self.add_clause(resolvent)

        # Mark all clauses containing the variable as inactive
        for clause in variable.positive.occurrences | variable.negative.occurrences:
            del self.clauses_by_index[clause.index]
            self.clauses.remove(clause)

        # Remove the variable from the set of variables
        del self.variables[variable.index]
