# QSP three-bit PARTITION proof study

The [full preprint for review](../hidden_parity/README.md) sharpens the earlier lower bound to the exact minimum.

Read the [four-page proof note](proof-study.pdf) for the mathematical statements and their scope. The construction studies a specific way of certifying failure by ruling out assignments to individual boundary bits. It also supplies a stronger exact solver for recognized layouts and an independent exact-count formula for the entire restricted input class.

## Replay

In this folder, use Python 3.10 or later.

```sh
python study.py
python affine_count.py
python z3_check.py
python check_examples.py
```

The first, second and fourth commands use the Python standard library. The third additionally uses the Z3 shared library through its C interface. On a system with a different solver build or a slower machine, a six-second timeout for an individual instance can return `unknown`. The stored Z3 record reported a definite answer for every check.

## Evidence

- `study.py` generates the two families, permutes rows and item order, reconstructs the seven virtual colors from the integers, and returns a checked integer witness for every feasible control. It includes the four-port gadget truth table, independent parity-image checks and tests of all seven line deletions.
- `affine_count.py` uses inclusion–exclusion and binary Gaussian elimination to count all subsets whose sum is half the total, treating equal-valued items as distinct by index. It compares with direct integer subset counts on 23,211 exhaustive small cases and 600 seeded cases. The formula includes exponentially many terms in the number of quartet rows.
- `z3_check.py` decodes each number in base eight and builds its own Boolean formula from the resulting digit rows. On the generated family each row has four items. Prohibiting any three true values and any three false values enforces exactly two. Z3 sees neither the hidden colors nor the structural recognizer's output.
- `examples.json` contains a 658-weight NO instance and a 658-weight YES control with a concrete subset. Each weight is an exact hexadecimal integer string. Indices in the witness are zero-based.
- `results.json`, `affine_results.json` and `z3_results.json` contain the recorded checks. Widths range from 1 to 51. The prototype ran three shuffles per family per width. Z3 used a fourth shuffle. Counts in the proof note are mathematical bounds or explicitly labelled check counts; the package does not benchmark the production QSP solver.

## Definitions

The input is a multiset of positive binary integers. Permitted set bits occupy positions divisible by three. Each weight contains at most three ones and each position occurs in at most four weights. A solution selects a subset whose sum equals that of its complement.

`solve_recognized(weights)` accepts only layouts passing its structural checks. Unsupported input raises `Unsupported`, distinct from a certified NO. `affine_count(weights)` handles every valid input in the restricted class. The explicit local lower bound applies to covers of the boundary-assignment cube by conflicts obtained directly from individual lines or proper subsystems, as defined in the proof note.
