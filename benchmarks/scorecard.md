# QSP exact solver across 120 days

QSP returned a verified optimum on **8 of 12** fixed instances with the code available July 28, 2026 and **12 of 12** with the November 25 revision. All eight cases that passed on both revisions ran faster. Their equally weighted geometric mean speedup was **59.25×**. The largest gain was the 20-variable dense integer QUBO, from **1.224 s to 1.710 ms**.

| Benchmark instance | Variables | Reference minimum | July 28 result | November 25 result | July median ms | November median ms | Verified speedup |
|---|---:|---:|---|---|---:|---:|---:|
| Dense symmetric integer | 12 | −120 | Pass | Pass | 4.8624 | 0.1292 | 37.65× |
| Dense symmetric integer | 16 | −136 | Pass | Pass | 77.0623 | 0.2800 | 275.17× |
| Dense symmetric integer | 20 | −295 | Pass | Pass | 1,224.4220 | 1.7099 | 716.08× |
| Dense fractional | 18 | −25.3824096008¹ | Pass | Pass | 311.6709 | 17.7673 | 17.54× |
| MaxCut, path | 13 | −12 | Pass | Pass | 9.6061 | 0.1458 | 65.89× |
| MaxCut, complete graph | 14 | −49 | Pass | Pass | 19.9411 | 0.1648 | 121.04× |
| MaxCut, sparse graph | 12 | −15 | Pass | Pass | 4.7910 | 0.1081 | 44.30× |
| One-hot equality, weak penalty | 3 | −12 | Rejected feasible instance | Pass | 0.0275 | 0.0606 | — |
| Asymmetric integer | 6 | −18 | Returned +3 | Pass | 0.0804 | 0.0353 | — |
| Asymmetric integer | 7 | −41 | Pass | Pass | 0.1538 | 0.0465 | 3.30× |
| Asymmetric integer | 8 | −23 | Returned −8 | Pass | 0.3191 | 0.0545 | — |
| Asymmetric integer | 9 | −31 | Returned −20 | Pass | 0.6139 | 0.0652 | — |

¹ Rounded for display. The exact reference is −14631962933735312782 / 576460752303423488. The verifier compares the witness energy to the exact optimum in integer units.

A pass requires a feasible binary witness that attains the independent reference minimum and a consistent reported objective. The oracle exhaustively evaluates the objective with integers or uses the known MaxCut value for the path and complete graph. A dash indicates a correctness repair. The baseline timing in that row measures how quickly an incorrect result returned. The asymmetric cases call the solver dispatcher directly. Normal API ingestion already symmetrized such matrices.

## Dates and timing

July 28 to November 25 is a 120-calendar-day window. The July 28 snapshot resolves to the July 20 main commit `c93293748678390206ac4462439a4b47d117c97e`. The next first-parent main commit landed August 1. The November snapshot is `d5b6f2c73220cb4a069a6aea8fc40d2332cf30a7`, whose Git tree is identical to the merged main commit `e18fe691e7fa0dc184549da852f268f933094c6e`. Both revisions were timed retrospectively on November 25.

Each revision ran twice in a fresh Python process. The order was July, November, November, July. Each process initialized the dispatcher and made five timed calls per case. Each cell reports the median of all ten dispatch-and-solve times for that revision. Input creation, oracle evaluation, witness verification and process startup were outside the timer. Speedup is the ratio of unrounded medians. Both snapshots used the same AMD Ryzen 7 9700X, Windows 11, Python 3.14.5, NumPy 2.4.6 and one numerical-library thread. Machine load and submillisecond timer variation can change the observed ratios.

The 12 rows are deterministic fixtures of the exact tier. The score measures that tier on those inputs. For example, the dense 20-variable case still considers 1,048,576 assignments. A proof for unrestricted inputs would require bounding the worst-case running time as a function of their encoded length.

## Verify the published statistics

From the repository root, run `python benchmarks/verify_timings.py` with Python 3.10 or newer. The script recalculates pass counts, medians and speedups from the [240 recorded solve times](raw_results.json). Re-timing the historical versions of the production solver requires access to those versions.
