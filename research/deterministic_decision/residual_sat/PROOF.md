# Why an ordered residual compiler can take superpolynomial time

The candidate decides SAT by building an ordered binary decision diagram for the satisfying assignments. Merging two prefixes is sound whenever they give the same Boolean function of the remaining variables. To prove polynomial worst-case time for this compiler, one would have to bound the number of distinct functions it constructs by a polynomial in the input length. The following family violates that bound for every choice of a single variable order.

## An explicit family

Let $m$ be even and at least 2. Use one variable per vertex of an $m\times m$ square grid. For each horizontal or vertical edge $uv$, include the clause $x_u\lor x_v$. The formula has $m^2$ variables and $2m(m-1)$ binary clauses. For the three-literal family used in the experiment, add a shared selector $z$. For every edge, include $(\neg z\lor x_u\lor x_v)$ and $(z\lor\neg x_u\lor\neg x_v)$. When $z=1$, the edge constraints reduce to the positive grid. When $z=0$, each edge must have at least one false endpoint.

**Claim.** In every grid-variable order there is a cut with at least $2^{\lceil m/80\rceil}$ different residual functions.

1. Split the order after half the grid variables. Give the first half color A and the second half color B. If at least $m/2$ rows contain both colors, each such row has a horizontal edge between colors. Otherwise each color occupies more vertices than all mixed rows combined, so an all-A row and an all-B row exist. Every column then has a vertical edge between colors. Either way there are at least $m/2$ crossing edges.

2. Greedily choose a crossing edge $a_i b_i$, with $a_i$ in A, then delete every crossing edge touching either endpoint or any of its neighbors. The grid has maximum degree four. The closed neighborhoods of the two endpoints contain at most ten vertices in total, each incident with at most four crossing edges. Thus each step removes at most forty crossing edges, including the chosen edge. The $k\ge\lceil m/80\rceil$ selected edges have no extra edges among their endpoints, within or across the cut.

3. For every subset $U\subseteq\{1,\ldots,k\}$, assign false to $a_i$ for $i\in U$ and true to every other A vertex. Every edge within A has a true endpoint. For any $j$, complete the assignment with all B variables true except $b_j$. The only possible edge with two false endpoints is $a_j b_j$. The result is false exactly when $j\in U$. Choosing $j$ in the symmetric difference of two subsets therefore distinguishes their residual functions.

4. After a fixed prefix, the node or terminal reached in an ordered diagram determines the entire suffix function. Pairwise different residuals must reach different nodes or terminals, even when reduction skips some variable tests. For the three-literal encoding, fix $z=1$ and skip its test in the diagram. The result is a diagram for the original grid in the grid variables' induced order. This operation cannot increase diagram size.

With conventional binary indices, the encoding length $L$ is $O(m^2\log m)$. For any constant $d$, $2^{m/80}$ eventually exceeds $L^d$. Explicitly constructing this diagram therefore takes superpolynomial time on the family. Stronger exponential lower bounds in the number of variables are known for bounded-degree expander graph CNFs. [Bova and Slivovsky, *On Compiling Structured CNFs to OBDDs*](https://arxiv.org/abs/1411.5494).

## What the result decides

Setting the selector and every grid vertex true gives a satisfying assignment a decision solver could return immediately. The lower bound applies to a compiler that represents all satisfying continuations under one common variable order, including an order chosen from the input. It settles the proposed polynomial bound for this candidate. Other decision algorithms and the general P versus NP question remain open. [Cook, *The P versus NP Problem*](https://www.claymath.org/library/monographs/MPPc.pdf).
