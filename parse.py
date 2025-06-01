"""Parse utilities for QDIMACS files."""

from typing import List, Literal
from dataclasses import dataclass

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


@dataclass
class QuantifierBlock:
    """Represents a quantifier block in a QDIMACS file."""
    bound_variables: List[int]
    quantifier_type: Literal["forall", "exists"]

    def is_forall(self) -> bool:
        """Return whether this is a forall quantifier block."""
        return self.quantifier_type == "forall"

    def is_exists(self) -> bool:
        """Return whether this is an exists quantifier block."""
        return self.quantifier_type == "exists"


@dataclass
class QDimacs:
    """Represents a QDIMACS file."""
    num_vars: int
    clauses: List[List[int]]
    quantifiers: List[QuantifierBlock]

    def __str__(self) -> str:
        """Return a string representation of the QDIMACS file."""
        return f"p cnf {self.num_vars} {len(self.clauses)}\n" + "\n".join(
            " ".join(str(lit) for lit in clause) + " 0" for clause in self.clauses
        )

    @staticmethod
    def parse(file_content: str) -> "QDimacs":
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
                quantifier_type = "forall"
                line = line[1:]
            elif line.startswith("e"):
                quantifier_type = "exists"
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


def parse_qdimacs(file_content: str) -> QDimacs:
    """Parse a QDIMACS file from string.

    This is a wrapper around QDimacs.parse for backward compatibility.
    """
    return QDimacs.parse(file_content)
