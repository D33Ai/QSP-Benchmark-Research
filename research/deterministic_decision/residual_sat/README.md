# An exact residual-function experiment for 3-SAT

**Result.** The deterministic classical solver correctly decides 3-SAT and can return a satisfying assignment. Its proposed polynomial worst-case bound fails. An explicit family of three-literal formulas forces superpolynomially many distinct residual functions under every variable order. This closes one route to proving P = NP. The general problem remains open.

## The candidate

After part of a formula has been assigned, its *residual function* maps each remaining assignment to true or false. The candidate tries to compress the search by sharing prefixes with identical residual functions. It chooses a variable order based on the input, then compiles the entire function as a reduced ordered binary decision diagram.

1. Normalize clauses, dropping tautologies, duplicates and any clause containing another.
2. Build the graph that connects variables occurring in the same clause. Repeatedly choose the next variable that minimizes the number of processed vertices still touching an unprocessed one. Ties favor more processed neighbors, then fewer unprocessed neighbors, then the smaller variable ID.
3. Substitute both values of the earliest active variable. Reuse previously computed syntactic residuals. Intern nodes by variable and the two child IDs, and skip tests with identical children. This implements exact sharing of equivalent Boolean functions for the fixed order. An explicit stack handles the recursion.
4. Return UNSAT for a false root. For a satisfiable root, repeatedly take a child other than false to recover a witness. Skipped variables can be false.

**Correctness.** The normalized clauses describe the same function as the input. By induction on the number of remaining variables, both child nodes represent the corresponding restrictions exactly. Testing the chosen variable therefore recovers the original function. Sharing identical nodes and skipping tests with equal children preserve this invariant. The only identically false root in the reduced diagram is the false terminal, so the decision and witness rules follow. Each substitution removes its variable from the residual, which proves termination.

For input bit length $L$ and $n$ distinct active variables there are at most $2^{n+1}-1$ visits in an unshared binary search tree. The work per residual before table lookups is polynomial in $L$. With balanced search trees in a bit model, the cost per lookup is also polynomial in $L$ since even the largest state IDs use $O(n)$ bits. This gives an exponential upper bound for the algorithm and explains where any proposed polynomial bound would have to come from. The implementation uses Python dictionaries with full-key equality. It never treats a hash collision as proof of equivalence.

## What the runs found

The oracle evaluates the original clauses directly on every assignment and checks both the diagram and the extracted witness. Two variable orders were checked per formula. The seed, exact counts and full grid results are in [results.json](results.json).

| Corpus | Formulas | SAT | UNSAT | Assignment checks across both orders |
|---|---:|---:|---:|---:|
| All subsets of the eight distinct signed three-literal clauses on three variables | 256 | 255 | 1 | 4,096 |
| Seeded three-literal formulas on 4, 6 and 8 variables | 120 | 77 | 43 | 26,880 |
| Empty, tautological, repeated-literal and mixed-width cases | 7 | 5 | 2 | 44 |
| **Total** | **383** | **337** | **46** | **31,020** |

All checks agreed. On a second family, the input consists of grid edges with a common selector. The table gives the **actual nonterminal nodes** instantiated during compilation. Every row yielded a satisfying assignment that passed direct evaluation.

| Grid | Variables including selector | Three-literal clauses | Selector first, row-major | Greedy boundary order |
|---|---:|---:|---:|---:|
| 2 × 2 | 5 | 8 | 13 | 13 |
| 3 × 3 | 10 | 24 | 59 | 55 |
| 4 × 4 | 17 | 48 | 181 | 163 |
| 5 × 5 | 26 | 80 | 483 | 433 |
| 6 × 6 | 37 | 120 | 1,165 | 1,045 |

For the 64 × 64 grid, a separately checked induced matching certifies at least $2^{32}$ distinct residuals for the row-major cut and $2^{924}$ for a checkerboard cut after fixing the selector. These are mathematical lower bounds obtained from the listed matching sizes. The large diagrams were never allocated. The proof covers **every order** on arbitrarily large even grids and yields a superpolynomial lower bound in encoded input length. On the same family, a direct decision strategy can immediately return an all-true witness. [Proof and prior work](PROOF.md)

## Reproduce

Run with Python 3.10 or newer from this directory. The experiment uses the standard library. The recorded seed and counts were generated with CPython 3.12.13.

```sh
python -m unittest -v test_residual_sat
python run_experiment.py --json results.json
python residual_sat.py path/to/instance.cnf
```

The last command accepts DIMACS with up to three literals per clause, including empty clauses. It prints the decision, true variable IDs of a witness for SAT, and structural counts. Omitted variables are false. The solver works on ordinary classical hardware. The measurements here are discrete operation counts for a research algorithm and stand independently of the QSP benchmark timings.
