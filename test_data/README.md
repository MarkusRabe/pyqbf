# Test Data for PyQBF

This directory contains example QDIMACS files for testing the QBF parser and solver.

## Files

### Satisfiable Formulas

- **`satisfiable_tautology.qdimacs`** - Simple tautology: `∃x.(x ∨ ¬x)`
  - Always satisfiable regardless of x's value
  - Tests basic existential quantifier with tautological clauses

- **`satisfiable_mixed_quantifiers.qdimacs`** - Mixed quantifiers: `∃x∀y.(x ∨ y)`
  - Satisfiable by setting x=true (then x∨y is true for any y)
  - Tests exists followed by forall quantifier

- **`classic_qbf_example.qdimacs`** - Classic example: `∀x.∃y.(x ∨ y) ∧ (¬x ∨ y)`
  - Satisfiable by setting y=true for any x
  - Common example from QBF literature

### Unsatisfiable Formulas

- **`unsatisfiable_example.qdimacs`** - Contradiction: `∀x∃y.(x ∨ y) ∧ (¬x ∨ ¬y) ∧ (x ∨ ¬y) ∧ (¬x ∨ y)`
  - Forces y to be both true and false for any x
  - Tests unsatisfiable QBF detection

### Classical SAT Formulas (No Quantifiers)

Classical SAT formulas are in DIMACS format (.dimacs) without quantifier blocks. DIMACS is a subset of QDIMACS, so the parser should handle them correctly.

- **`classical_sat_satisfiable.dimacs`** - Simple satisfiable: `x1`
  - Classical DIMACS format without quantifiers
  - Satisfiable by setting x1=true

- **`classical_sat_unsatisfiable.dimacs`** - Contradiction: `x1 ∧ ¬x1`
  - Classical SAT formula that's unsatisfiable
  - Tests classical DIMACS parsing

- **`classical_sat_complex.dimacs`** - Multiple variables: `(x1 ∨ x2) ∧ (¬x1 ∨ x2) ∧ (x1 ∨ ¬x2)`
  - More complex classical SAT formula
  - Satisfiable with x1=true, x2=true

### Complex Examples

- **`complex_alternating.qdimacs`** - Alternating quantifiers: `∀x₁∃x₂∀x₃∃x₄.(x₁ ∨ x₂ ∨ x₃) ∧ (¬x₁ ∨ ¬x₃ ∨ x₄)`
  - Tests alternating ∀∃∀∃ quantifier pattern
  - More complex quantifier structure

- **`large_formula.qdimacs`** - Larger formula with 5 variables
  - Tests multiple variables per quantifier block
  - More clauses and variables

## Usage

These files are used by:
- `file_test.py` - Tests file reading and parsing functionality
- Manual testing with `main.py` - e.g.,
  - `python main.py test_data/satisfiable_tautology.qdimacs`
  - `python main.py test_data/classical_sat_satisfiable.dimacs`
- Integration testing of the complete pipeline

## File Format Support

The parser supports both:
- **QDIMACS format** (.qdimacs) - Quantified Boolean Formulas with quantifier blocks
- **Classical DIMACS format** (.dimacs) - Standard SAT formulas without quantifiers

## Expected Results

Currently, the placeholder solver returns "UNSAT" for all formulas. When a real solver is implemented:
- **Satisfiable formulas** (both QBF and SAT) should return "SAT"
- **Unsatisfiable formulas** (both QBF and SAT) should return "UNSAT"
