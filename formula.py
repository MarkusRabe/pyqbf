"""Data structures for QBF formulas."""

from typing import List, Dict, Set, Sequence, FrozenSet, Iterable
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
    # Universal variables that this variable depends on (i.e. universal
    # quantifiers that are quantified at a lower level)
    dependencies: Set["Variable"] = field(default_factory=set)

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
        self.variables_by_index: Dict[VariableIndex, Variable] = {}
        self.clauses: Set[Clause] = set()
        self.clauses_by_index: Dict[ClauseIndex, Clause] = {}

        # Largest variable/clause index that MAY be in use.
        # 0 is not a valid variable index.
        self._largest_used_variable_index = 1
        self._largest_used_clause_index = 0

        universal_variables: Set[Variable] = set()
        for quantifier in qdimacs.quantifiers:
            for variable in quantifier.bound_variables:
                if quantifier.is_forall():
                    universal_variables.add(variable)
                if quantifier.is_exists():
                    self.create_fresh_variable(
                        variable, quantifier.quantifier_type, universal_variables
                    )
                else:
                    self.create_fresh_variable(variable, quantifier.quantifier_type)

        for variable_index in range(1, qdimacs.num_vars + 1):
            if variable_index not in self.variables_by_index:
                # assuming that these variables are existential and can't depend on any universal variables
                self.create_fresh_variable(variable_index)

        for index, clause in enumerate(qdimacs.clauses):
            for literal in clause:
                var_index = abs(literal)
                if var_index not in self.variables_by_index:
                    self.create_fresh_variable(var_index)
            clause = self.create_clause_from_qdimacs(clause, index)
            self.add_clause(clause)

    @property
    def variables(self) -> Iterable[Variable]:
        """Return the set of variables in this formula."""
        return self.variables_by_index.values()

    def next_fresh_variable_index(self) -> int:
        """Return the next fresh variable index."""
        while self._largest_used_variable_index in self.variables_by_index:
            self._largest_used_variable_index += 1
        return self._largest_used_variable_index

    def create_fresh_variable(
        self,
        index: int | None = None,
        quantifier: QuantifierType = QuantifierType.EXISTS,
        dependencies: Set[Variable] | None = None,
    ) -> Variable:
        """Create a new variable with the given quantifier."""
        index = index or self.next_fresh_variable_index()
        assert index not in self.variables_by_index
        dependencies = dependencies or set()
        self.variables_by_index[index] = Variable(index, quantifier, dependencies)
        return self.variables_by_index[index]

    def next_fresh_clause_index(self) -> int:
        """Return the next fresh clause index."""
        while self._largest_used_clause_index in self.clauses_by_index:
            self._largest_used_clause_index += 1
        return self._largest_used_clause_index

    def get_literal_by_index(self, literal_index: int) -> Literal:
        """Return the literal with the given QDIMACS index."""
        variable_index = abs(literal_index)
        is_positive = literal_index > 0
        return self.variables_by_index[variable_index].get_literal(is_positive)

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
        if self.is_clause_subsumed(clause):
            return
        self.clauses.add(clause)
        self.clauses_by_index[clause.index] = clause
        for literal in clause.literals:
            literal.occurrences.add(clause)

    def contains_empty_clause(self) -> bool:
        """Return whether this formula contains the empty clause."""
        return self.generate_empty_clause() in self.clauses

    def resolve(self, clause1: Clause, clause2: Clause, variable: Variable) -> Clause:
        """Resolve two clauses with respect to a variable."""
        assert variable.index in self.variables_by_index
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
        header = f"p cnf {len(self.variables_by_index)} {len(self.clauses)}"
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
        assert variable.index in self.variables_by_index

        # Collect all resolvents first
        resolvents = []
        for positive_clause in variable.positive.occurrences:
            for negative_clause in variable.negative.occurrences:
                resolvent = self.resolve(positive_clause, negative_clause, variable)
                # apply universal reduction
                resolvent = self.universal_reduction(resolvent)
                resolvents.append(resolvent)

        # Mark all clauses containing the variable as inactive
        for clause in variable.positive.occurrences | variable.negative.occurrences:
            if clause.index in self.clauses_by_index:
                del self.clauses_by_index[clause.index]
            if clause in self.clauses:
                self.clauses.remove(clause)

        # Remove the variable from the set of variables
        del self.variables_by_index[variable.index]

        # Now add all the resolvents
        for resolvent in resolvents:
            self.add_clause(resolvent)

    def is_propositional_formula(self) -> bool:
        """Return whether this formula is quantifier-free."""
        if all(quantifier.is_exists() for quantifier in self.quantifiers):
            return True
        return False

    def universal_reduction(self, clause: Clause) -> Clause:
        """Apply universal reduction to a clause.

        Universal reduction removes universally quantified literals from a clause
        if the universal variable is quantified to the right of all existential
        variable in the same clause.
        """
        if not self.quantifiers:
            # No quantifiers, return clause as-is
            return clause

        # Build quantifier level mapping and type mapping
        var_to_level = {}
        var_to_quantifier = {}
        for level, quantifier_block in enumerate(self.quantifiers):
            for var_index in quantifier_block.bound_variables:
                var_to_level[var_index] = level
                var_to_quantifier[var_index] = quantifier_block.quantifier_type

        # Separate universal and existential literals
        universal_literals = []
        existential_literals = []

        for literal in clause.literals:
            var_index = literal.variable
            if var_index in var_to_quantifier:
                if var_to_quantifier[var_index] == QuantifierType.FORALL:
                    universal_literals.append(literal)
                else:
                    existential_literals.append(literal)
            else:
                # Treat unquantified variables as existential
                existential_literals.append(literal)

        # Apply universal reduction rule:
        # Remove universal literals that are at a higher level (right) than ANY existential literal
        reduced_literals = list(existential_literals)

        for universal_lit in universal_literals:
            universal_level = var_to_level.get(universal_lit.variable, -1)

            # Check if this universal literal can be reduced
            # It can be reduced if it's at a higher level than ANY existential literal
            can_reduce = False
            for existential_lit in existential_literals:
                existential_level = var_to_level.get(
                    existential_lit.variable, float("inf")
                )
                # If universal is at a higher level than this existential, it can be reduced
                if universal_level > existential_level:
                    can_reduce = True
                    break

            if not can_reduce:
                # Keep the universal literal
                reduced_literals.append(universal_lit)

        # Create new clause with reduced literals
        if len(reduced_literals) == len(clause.literals):
            # No reduction possible, return original clause
            return clause

        # Create a new clause with the reduced literals
        # We need to make sure the literals reference the correct variables
        corrected_literals = []
        for lit in reduced_literals:
            if lit.variable in self.variables_by_index:
                # Use the existing literal from the variable
                var = self.variables_by_index[lit.variable]
                corrected_literals.append(var.get_literal(lit.is_positive))
            else:
                # Variable doesn't exist anymore, skip this literal
                continue

        if not corrected_literals:
            # If no literals remain, return an empty clause
            # return Clause.from_literals(
            #     [], self.next_fresh_clause_index(), is_original=False
            # )
            return self.generate_empty_clause()

        new_clause = Clause.from_literals(
            corrected_literals, self.next_fresh_clause_index(), is_original=False
        )
        return new_clause
