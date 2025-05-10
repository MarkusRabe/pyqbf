"""Entry point for the solver. Parses argument to read a file and call the lib code."""

import argparse
import sys

import lib


def main():
    """Entry point for the solver."""
    parser = argparse.ArgumentParser(description="Solve a quantified boolean formula.")
    parser.add_argument(
        "file", metavar="FILE", type=str, help="The file to read the problem from. In QDIMACS format."
    )
    args = parser.parse_args()

    try:
        with open(args.file) as file:
            file_content = file.read()
    except FileNotFoundError:
        print(f"File {args.file} not found.", file=sys.stderr)
        sys.exit(1)

    try:
        solution = lib.solve_file(file_content)
    except ValueError as e:
        print(f"Invalid puzzle: {e}", file=sys.stderr)
        sys.exit(1)

    print(solution)


if __name__ == "__main__":
    main()
