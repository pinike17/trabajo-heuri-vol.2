## Quick orientation

This repository contains small GLPK/GMPL optimization models and Python helpers that
produce GLPK data files and invoke `glpsol`. The most relevant files are under
`parte-2/`:

- `parte-2/gen-1.py` — produces a `.dat` file for `parte-2-1.mod` and runs `glpsol`.
- `parte-2/gen-2.py` — produces a `.dat` file for `parte-2-2.mod` and runs `glpsol`.
- `parte-2/parte-2-1.mod`, `parte-2/parte-2-2.mod` — GMPL models consumed by the scripts.

Keep in mind: the scripts expect `glpsol` on PATH and write `glpsol.out` and
`solution.sol` into the same directory as the produced `.dat` file.

## How to run (developer-friendly)

- Generate a `.dat` and run the model with `gen-1.py`:

  python parte-2/gen-1.py INPUT_FILE OUTPUT.dat

  - INPUT_FILE (example) must be 4 non-empty lines (comments starting with `#` are ignored):
    1) "n m" (integers)
    2) "kd kp" (floats)
    3) m values: distances d_i (floats)
    4) m values: passengers p_i (numbers; integers preferred)

- Generate a `.dat` and run the model with `gen-2.py`:

  python parte-2/gen-2.py INPUT_FILE OUTPUT.dat

  - INPUT_FILE format (line-oriented):
    1) "n m u" (integers)
    2..(m+1) ) m lines: passenger overlap matrix c (m numbers per line)
    (m+2).. ) u lines: slot availability o (n integers per line, 0/1)

Notes: `gen-1.py` strips `#` comments and blank lines. `gen-2.py` strips blank lines but does not specially treat `#` comments.

## Important project conventions & patterns

- The Python scripts build GMPL `set` and `param` blocks enumerating indices starting at 1
  (BUS indices 1..m, SLOTS indices 1..n). Follow the same 1-based indexing when creating test `.dat` files.
- Variable names in the models follow `x[...]` and `y[...]` convention. The scripts parse `glpsol` textual output by looking for the
  "No. Column name" table and reading column values; that parsing assumes `glpsol` default textual layout.
- Output behavior: after running `glpsol`, each script prints a short summary line: "<objective or N/A> <num_vars> <num_cons>"
  followed by per-bus assignment lines. Tests and CI can assert on this textual contract.

## Debugging tips (fast)

- If `glpsol` fails, run the same command the script uses manually to see full output:
  glpsol -m <model.mod> -d <file.dat> --write solution.sol -o glpsol.out

- Inspect `glpsol.out` for the lines starting with "Objective:" and the "No. Column name" table
  (the scripts depend on these sections for parsing). If the table layout changes, update the regexes in
  `parte-2/gen-1.py` and `parte-2/gen-2.py` (search for the `re.match(...)` patterns).

- Common pitfalls:
  - Ensure the number of distances/passenger entries equals `m` for `gen-1.py` (script validates this).
  - Use integer 0/1 for availability matrix in `gen-2.py` (script writes `o` as given).
  - If model path warnings appear, confirm the `.mod` files are present next to the genscripts.

## Where to extend or change behavior

- To support a different solver or output format, update `run_glpsol()` in the two scripts. The code centralizes subprocess invocation there.
- To change input parsing rules, update `parse_input()` in each `gen-*.py`. Note `gen-1.py` intentionally ignores `#` comments while `gen-2.py` does not.

## Files to inspect for examples

- `parte-2/gen-1.py` — shows writing of `param d` and `param p`, handling of floats vs ints, output contract.
- `parte-2/parte-2-1.mod` — example of a minimal GMPL model with `x[i,s]` and `y[i]` binaries.
- `parte-2/gen-2.py` and `parte-2/parte-2-2.mod` — demonstrate multi-index variables `x[i,s,w]` and linking constraints used by the project.

If anything above is unclear or you'd like more examples (sample INPUT files, unit tests, or a CI job that runs `glpsol`), tell me which part to expand and I'll iterate.
