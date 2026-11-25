# Can QSP's exact search be made polynomial on every input?

We tested three deterministic classical approaches. Two give correct decisions on unrestricted inputs to an NP-complete problem. Each has an explicit family on which its running time grows superpolynomially. The third gives an incorrect UNSAT answer on a three-variable formula. The experiments establish which proposed shortcuts fail and identify a graph class where the Max-Cut route has a polynomial guarantee. The general P versus NP question remains open. [Cook's formal problem statement](https://www.claymath.org/library/monographs/MPPc.pdf)

| Approach | Result on unrestricted inputs | Where the proposed polynomial bound fails |
|---|---|---|
| [Max-Cut by conditioning and minimum cut](maxcut/README.md) | Exact YES or NO for signed integer weights and integer thresholds. Runs in polynomial time when the computed cover of conflicting edges has logarithmic size in the input length. | For a positive unit-weight complete graph on $n\ge5$ vertices, the first unattainable threshold forces this procedure to make exactly $2^{n-3}$ minimum-cut calls. |
| [3-SAT by sharing equivalent residual functions](residual_sat/README.md) | Exact YES or NO. A YES answer includes a satisfying assignment. | On an $m\times m$ grid family, every fixed variable order chosen for that input requires at least $2^{\lceil m/80\rceil}$ distinguishable suffix functions. The input uses $O(m^2\log m)$ bits. [Proof](residual_sat/PROOF.md) |
| [SAT by parity of weighted solutions](weight_isolation/WEIGHT_ISOLATION.md) | A nonzero coefficient is a sound YES signal. Some satisfiable inputs give all-zero coefficients. | Models `110` and `001` cancel under weights `(1,2,3)`. A two-model formula can force the same failure for any single formula-independent vector of positive weights with polynomial total weight, for sufficiently many variables. |

## The Max-Cut experiment on QSP's own fixtures

The decision solver answered whether each of the three scorecard graphs can achieve its reference maximum and then whether it can beat that maximum by one. We checked every YES witness against the original edge list. The counts below measure calls to a classical minimum-cut algorithm. They are independent of the wall-clock timings for QSP's exact tier. [12-case benchmark scorecard](../../benchmarks/scorecard.md)

| Graph | Verified maximum cut | Cover size | Minimum-cut calls to answer YES at the maximum | Minimum-cut calls to answer NO one above |
|---|---:|---:|---:|---:|
| Path, 13 vertices | 12 | 0 | 0 | 0 |
| Sparse graph, 12 vertices | 15 | 1 | 1 | 1 |
| Complete graph, 14 vertices | 49 | 12 | 32 | 2,048 |

The sparse case shows what the cover buys. Fixing one conflicting vertex leaves an ordinary minimum-cut problem, and global complement symmetry removes the second assignment to that vertex. On the complete graph, even the best choice of signs leaves at least 12 vertices in the cover. A specialized formula solves the unit-weight complete graph directly. The lower bound here applies to the implemented algorithm and its proposed uniform cover-size bound.

## Verification and replay

From the repository root, run the commands below with Python 3.10 or newer. The experiments and tests use only the standard library.

```sh
python -m research.deterministic_decision.replay_qsp_maxcut
python -m unittest discover -s research/deterministic_decision/maxcut
python -m unittest discover -s research/deterministic_decision/residual_sat
python research/deterministic_decision/residual_sat/run_experiment.py
python research/deterministic_decision/weight_isolation/weight_isolation.py
```

The Max-Cut tests include all 729 signed four-vertex graphs with unit or zero edge weights, 192 seeded multigraphs, and weights beyond machine-integer precision. For 3-SAT, 383 formulas produced 337 SAT and 46 UNSAT results. All 31,020 truth-table comparisons agreed with direct evaluation. An additional DIMACS command-line test used 20 connected prism parity instances, ten SAT and ten UNSAT, up to 36 variables and 96 clauses. On those graphs feasibility is known independently because every edge contributes to the parity at two endpoints, and paths can realize any even set of charged vertices.
