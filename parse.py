"""Parse utilities for QDIMACS files."""

from typing import List, Sequence
from enum import Enum


class QuantifierType(Enum):
    """Enum for quantifier types in QDIMACS files."""
    FORALL = "forall"
    EXISTS = "exists"


class QDimacsError(Exception):
    """Base class for exceptions in this module."""
    pass


class QDimacsParseError(QDimacsError):
    """Exception raised for errors while parsing a QDIMACS file.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str):
        self.message = message


class QuantifierBlock:
    """Represents a quantifier block in a QDIMACS file."""
    
    def __init__(self, bound_variables: List[int], quantifier_type: QuantifierType):
        self.bound_variables = bound_variables
        self.quantifier_type = quantifier_type

    def is_forall(self) -> bool:
        """Return whether this is a forall quantifier block."""
        return self.quantifier_type == QuantifierType.FORALL

    def is_exists(self) -> bool:
        """Return whether this is an exists quantifier block."""
        return self.quantifier_type == QuantifierType.EXISTS
    
    def __eq__(self, other) -> bool:
        """Return whether this QuantifierBlock is equal to another."""
        if not isinstance(other, QuantifierBlock):
            return False
        return (self.bound_variables == other.bound_variables and 
                self.quantifier_type == other.quantifier_type)
    
    def __repr__(self) -> str:
        """Return a string representation of this QuantifierBlock."""
        return f"QuantifierBlock({self.bound_variables}, {self.quantifier_type})"


class QDimacs:
    """Represents a QDIMACS file."""

    def __init__(self, num_vars: int, clauses: Sequence[List[int]] = (), quantifiers: Sequence[QuantifierBlock] = ()):
        """Initialize a QDimacs instance.

        Args:
            num_vars: Number of variables in the formula
            clauses: List of clauses, where each clause is a list of literals
            quantifiers: List of quantifier blocks
        """
        self.num_vars: int = num_vars
        self.clauses: List[List[int]] = list(clauses)
        self.quantifiers: List[QuantifierBlock] = list(quantifiers)
    
    def copy(self) -> "QDimacs":
        """Return a copy of this QDimacs instance."""
        return QDimacs(self.num_vars, self.clauses, self.quantifiers)

    def __str__(self) -> str:
        """Return a string representation of the QDIMACS file."""
        return f"p cnf {self.num_vars} {len(self.clauses)}\n" + "\n".join(
            " ".join(str(lit) for lit in clause) + " 0" for clause in self.clauses
        )
    
    def __eq__(self, other) -> bool:
        """Return whether this QDimacs is equal to another."""
        if not isinstance(other, QDimacs):
            return False
        return (self.num_vars == other.num_vars and 
                self.clauses == other.clauses and 
                self.quantifiers == other.quantifiers)
    
    def __repr__(self) -> str:
        """Return a string representation of this QDimacs."""
        return f"QDimacs({self.num_vars}, {self.clauses}, {self.quantifiers})"



def from_qdimacs(file_content: str) -> QDimacs:
    """Parse a QDIMACS file from string."""
    lines = file_content.splitlines()
    # Remove comments and empty lines
    lines = [line.strip() for line in lines if line.strip() and not line.startswith("c")]

    if not lines:
        raise QDimacsParseError("Empty file")

    header = lines[0].split()
    if header[0] != "p":
        raise QDimacsParseError("Invalid header")

    if len(header) < 2 or header[1] != "cnf":
        raise QDimacsParseError("Only cnf format is supported")

    if len(header) != 4:
        raise QDimacsParseError("Invalid header")

    try:
        num_vars = int(header[2])
        num_clauses = int(header[3])
    except ValueError:
        raise QDimacsParseError("Invalid header")

    if num_vars <= 0:
        raise QDimacsParseError("Invalid number of variables")

    if num_clauses < 0:
        raise QDimacsParseError("Invalid number of clauses")

    clauses = []
    quantifiers = []
    for line in lines[1:]:
        if line.startswith("a"):
            quantifier_type = QuantifierType.FORALL
            line = line[1:]
        elif line.startswith("e"):
            quantifier_type = QuantifierType.EXISTS
            line = line[1:]
        else:
            quantifier_type = None

        if quantifier_type is not None:
            try:
                variables = line.split()
                # Quantifier blocks must end with 0
                if not variables or variables[-1] != "0":
                    raise QDimacsParseError("Quantifier blocks must end with 0")
                variables = variables[:-1]
                if not variables:
                    raise QDimacsParseError("Empty quantifier block")
                quantifiers.append(QuantifierBlock([int(literal) for literal in variables], quantifier_type))
            except ValueError:
                raise QDimacsParseError("Invalid quantifier")
            continue

        literals = line.split()
        if literals[-1] != "0":
            raise QDimacsParseError("Clauses must end with 0")

        try:
            clause = [int(literal) for literal in literals[:-1]]
        except ValueError:
            raise QDimacsParseError("Invalid literal")

        if not clause:
            raise QDimacsParseError("Empty clause")

        if any(literal == 0 for literal in clause):
            raise QDimacsParseError("Clauses must not contain 0")

        if any(abs(literal) > num_vars for literal in clause):
            raise QDimacsParseError("Variable out of range")

        if clause in clauses:
            raise QDimacsParseError("Duplicate clause")

        clauses.append(clause)

    return QDimacs(num_vars, clauses, quantifiers)