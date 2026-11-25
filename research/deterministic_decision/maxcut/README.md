# Can sign switching make every Max-Cut decision polynomial?

The decision problem asks whether some cut of an undirected graph has total weight at least the binary integer threshold T. The unweighted positive case is already NP-complete. The interface accepts a vertex count n, an edge list with signed integer weights, and an integer threshold. The complexity bound uses the standard explicit-graph encoding, which counts all n vertices, including isolates. Parallel edges add and self-loops contribute zero. A YES result includes the cut. For QSP's minimization convention, minimizing $-\sum_{uv} w_{uv}(x_u+x_v-2x_ux_v)$ is equivalent to maximizing the cut.

## Construction

1. Start with the best possible contribution of each edge in isolation. Their sum is U = Σ max(w, 0). A positive edge prefers opposite bits, a negative edge equal bits. Violating a preference loses |w| from U.
2. Choose a spanning forest by deterministic breadth-first search and assign bits g that satisfy every forest edge. Write xᵤ = yᵤ XOR gᵤ. In the y variables let F be the edges that still prefer opposite bits. Pick a vertex cover C of F by repeatedly taking a vertex of maximum uncovered degree, breaking ties by vertex ID. Write k = |C|.
3. Enumerate assignments to C, fixing the first bit to zero because complementing every bit preserves the cut. With C pinned, each free/free edge prefers equality and contributes a nonnegative disagreement cost. Put that weight on an undirected network edge. For each fixed/free edge, a terminal arc of the same capacity charges its unary disagreement cost. Fixed/fixed contributions are constant within this assignment. An exact s–t minimum cut now minimizes the total loss. Restore the original bits and check the integer objective on the original graph. Return YES when it reaches T, or NO when the enumeration finishes.

An empty F gives a certified optimum U straight from the forest assignment. A nonempty F contains an edge conflicting with the parity on its forest path. Every assignment therefore loses at least the smallest absolute nonzero edge weight. The implementation first tests explicit witnesses and this upper bound.

## Correctness and complexity

For a fixed assignment on C, source-side free vertices have bit 0. An undirected pair edge crosses precisely when its endpoint bits differ. A source-to-vertex arc charges bit 1, and a vertex-to-sink arc charges bit 0. Every crossing arc therefore accounts for its exact preference violation, up to the fixed/fixed constant. The max-flow/min-cut theorem proves the best completion for each pinning. Every feasible cut or its global complement appears in at least one enumerated branch, which proves completeness for all integer thresholds.

Let L be the total binary input length, counting the explicitly represented vertices, edge endpoints, weights and threshold. Let b bound the bits of the sum of all absolute input weights plus one. Flow has O(n) vertices and O(m+n) arcs for m input edges. Edmonds–Karp uses O((n+2)(m+n+2)²) arithmetic operations per call, independently of capacity values. Each intermediate capacity and objective needs O(b) bits. Graph preparation and greedy cover construction are polynomial in L. With at most 2^max(k−1,0) calls, the deterministic total bit complexity is 2^max(k−1,0) poly(L). In particular it is polynomial on every class with k ≤ c log₂ L for a fixed c. This bound uses the computed cover, so recognizing a fast instance requires no optimal-cover oracle.

## Where the attempted extension fails

Take the complete graph Kₙ with unit positive edges and T = floor(n²/4)+1, for n ≥ 5. A cut with a vertices on one side has value a(n−a), so T is one above optimum. This threshold passes the solver's initial upper bound. Breadth-first search creates a star; all non-root vertices get the same gauge bit, so F is a clique on n−1 vertices. Its greedy cover has k = n−2, and this NO input forces exactly 2^(n−3) minimum-cut calls. The count grows superpolynomially in the explicit adjacency-list input size O(n² log n).

**Choosing a better gauge or the minimum cover cannot fix this enumeration.** For any gauge with two nonempty color classes of sizes a and n−a on a positive complete graph, F is the union of two cliques. Every cover has at least (a−1)+(n−a−1) = n−2 vertices. A one-color gauge needs n−1. This lower bound also holds with arbitrary positive weights on these edges. On every such graph, threshold OPT+1 forces the implemented procedure through its enumeration for n ≥ 5, since every cut omits at least four positive edges and the initial upper bound deducts only one minimum edge weight. The closed formula solves the unit-weight family directly. This lower bound applies to the implemented decision procedure and the proposed universal small-cover lemma; it places no restriction on algorithms using other bounds or structure.

## Reproduction

From this directory, run `python test_gauge_maxcut.py` and `python test_gauge_maxcut.py --benchmark`. Tests compared witness and NO decisions at the exact optimum and one above it for all 729 four-vertex graphs with edge weights in {−1, 0, 1}, 192 seeded signed multigraphs up to nine vertices, and a graph with 101-digit weights. They also checked a 100-vertex even cycle (optimum 700, zero flow calls), empty input, malformed input and clique branch counts.

The following are same-machine medians of five calls per size on CPython 3.14.5. The branch counts are exact.

| Vertices | Edges | NO threshold | Cover | Min-cut calls | Median ms |
|---:|---:|---:|---:|---:|---:|
| 5 | 10 | 7 | 3 | 4 | 0.044 |
| 7 | 21 | 13 | 5 | 16 | 0.162 |
| 9 | 36 | 21 | 7 | 64 | 0.716 |
| 11 | 55 | 31 | 9 | 256 | 3.152 |
| 13 | 78 | 43 | 11 | 1,024 | 14.836 |
| 15 | 105 | 57 | 13 | 4,096 | 68.838 |

The model uses classical switching and network-flow techniques. See [Edmonds and Karp, 1972](https://doi.org/10.1145/321694.321699) for the flow algorithm and [Kolmogorov and Zabih, 2004](https://doi.org/10.1109/TPAMI.2004.1262177) for graph-representable binary energies.
