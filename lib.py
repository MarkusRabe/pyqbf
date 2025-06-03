"""QBF solver library."""

import parse
import formula


def solve_file(file_content: str) -> str:
    """Solve a QBF given in QDIMACS format."""
    puzzle = parse.from_qdimacs(file_content)
    return solve(puzzle)


def solve(puzzle: parse.QDimacs) -> str:
    """Solve a QBF puzzle."""
    return solve_by_variable_elimination(puzzle)


def solve_by_variable_elimination(puzzle: parse.QDimacs) -> str:
    """Solve a QBF puzzle by eliminating variables."""
    # Create the formula
    phi = formula.Formula(puzzle)

    # Eliminate the variables
    for variable in list(phi.variables):
        phi.eliminate_variable(variable)
        if phi.contains_empty_clause():
            return "UNSAT"

    return "SAT"
