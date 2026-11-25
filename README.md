# QSP benchmark results and deterministic search experiments

**QSP found the verified optimum on all 12 benchmark instances on November 25, 2026, up from 8 of 12 for the version available July 28.** Across the eight instances both versions solved correctly, the geometric mean speedup was **59.25×**. The largest gain was a 20-variable integer QUBO, from **1,224.42 ms to 1.71 ms**. Both revisions ran on the same classical CPU. [Download the one-page findings (PDF)](QSP_120_Day_Findings.pdf)

## Benchmark evidence

The retrospective compares two versions of QSP's exact solver on a fixed set of 12 inputs. Each reported time is the median of ten solves. Four earlier results failed independent verification. Those cases enter the correctness comparison only. The 20-variable example still considers all 1,048,576 assignments. [Full scorecard and methodology](benchmarks/scorecard.md) · [All 240 timing observations (JSON)](benchmarks/raw_results.json)

## P versus NP investigation

We built two deterministic classical algorithms that return exact decisions for unrestricted inputs to their respective problems. Each algorithm has a family of inputs that takes superpolynomial time. A third strategy fails a correctness test on three variables. The general P versus NP problem remains open. [Research report](research/deterministic_decision/README.md)

| Approach | Finding |
|---|---|
| [Weighted Max-Cut](research/deterministic_decision/maxcut/README.md) | Polynomial time when a computed set of vertices covering conflicting edges has logarithmic size. On a 15-vertex complete graph the solver used 4,096 minimum cuts to rule out 57, one above the maximum. |
| [Residual-function 3-SAT](research/deterministic_decision/residual_sat/README.md) | All 31,020 truth-table comparisons agreed. An explicit grid family forces superpolynomial diagram size for every variable order. [Proof](research/deterministic_decision/residual_sat/PROOF.md) |
| [Weighted model parity](research/deterministic_decision/weight_isolation/WEIGHT_ISOLATION.md) | Two satisfying assignments can have equal weight and cancel. A concrete three-variable example exposes the error. |

## Reproduce the public results

From the repository root with Python 3.10 or newer, these standard-library commands recalculate the timing summary, replay the two-sided Max-Cut decisions, and test the SAT and Max-Cut research implementations. The scorecard includes the workstation and measurement details needed to interpret the historical samples. Re-running the historical solver measurements themselves requires the corresponding production versions.

```sh
python benchmarks/verify_timings.py
python -m research.deterministic_decision.replay_qsp_maxcut
python -m unittest discover -s research/deterministic_decision/maxcut
python -m unittest discover -s research/deterministic_decision/residual_sat
python research/deterministic_decision/residual_sat/run_experiment.py
python research/deterministic_decision/weight_isolation/weight_isolation.py
```
