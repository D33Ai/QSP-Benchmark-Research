# Can weighted model parity decide SAT?

**Finding.** A satisfiable formula with just three variables defeats a deterministic parity test using weights $(1,2,3)$. The construction extends to every single formula-independent choice of positive integer weights whose total is polynomial in the variable count. A repaired algorithm must both choose weights that expose a model on every satisfiable input and compute the resulting parity information efficiently from a CNF.

## The proposed decision test

Let $F$ be a CNF on $n$ variables. Over the two-element field, define

$$
P_{F,w}(t)=\sum_{a:\ F(a)=1} t^{\sum_{i=1}^n w_i a_i}\quad\text{in }\mathbb F_2[t].
$$

The coefficient at degree $j$ is one precisely when an odd number of satisfying assignments has weight $j$. A nonzero coefficient proves satisfiability. One deterministic candidate is to choose a small fixed weight vector for each $n$, compute the polynomial, and return UNSAT if it is zero.

For example, let $F$ impose $x=y$ and $x\ne z$. Its clauses are $(\neg x\lor y),(x\lor\neg y),(x\lor z),(\neg x\lor\neg z)$. Its only models give the following contributions.

| Assignment $(x,y,z)$ | Weight under $(1,2,3)$ | Weight under $(1,2,4)$ |
|---|---:|---:|
| $(1,1,0)$ | 3 | 3 |
| $(0,0,1)$ | 3 | 4 |

With the first vector, $t^3+t^3=0$ in $\mathbb F_2[t]$. The test would answer UNSAT. With the second vector, $t^3+t^4$ exposes both models.

## The general collision

Let $S=\sum_i w_i$. If $2^n>S+1$, two different assignments $a,b$ have the same weight by the pigeonhole principle. Build a CNF whose only models are $a,b$. Pin all coordinates on which they agree using unit clauses. Choose any coordinate $p$ on which they differ. For each other differing coordinate $i$, enforce $x_i=x_p$ if $a_i=a_p$, or $x_i=\neg x_p$ otherwise, using two binary clauses. Each choice of $x_p$ now determines a full satisfying assignment. The formula has at most $2(n-1)$ clauses of width at most two, so it is a valid input to SAT with clause width at most three. Its two equal-degree monomials cancel. Any polynomial bound on $S$ eventually meets the inequality.

The same counting argument applies to a fixed list of weight vectors with totals $S_1,\ldots,S_r$ whenever $\prod_{j=1}^r(S_j+1)<2^n$. Two assignments then have identical vectors of total weights. The argument loses force for longer lists. For example, all ones plus the $n$ weightings that individually raise one coordinate from one to two separate every pair of distinct assignments in at least one test. Formulas with exactly two models therefore cannot disprove that entire list. With four models the list can already fail. $(x_1\ne x_2)\land(x_3\ne x_4)$ gives four equal-weight assignments for all ones. Raising any single coordinate splits them into two pairs of equal weight.

## Which repairs are still possible?

| Change | What can be established | Remaining proof obligation |
|---|---|---|
| Choose weights using the formula | Every satisfiable formula admits small isolating weights. For an inclusion-minimal satisfying support $A$, use weight 1 on $A$ and $n+1$ elsewhere. Every different model contains an outsider and costs more. | Construct suitable weights in deterministic polynomial time from the CNF. The existence argument begins with a model. |
| Try several deterministic weightings | One nonzero polynomial in the list suffices to accept. A sufficiently long list escapes the counting counterexample. | Produce a polynomial-size list uniformly in polynomial time and prove coverage for every satisfiable input of the given length. |
| Draw random weights | The isolation lemma gives a unique minimum-weight model with probability at least $1/2$ when the weights are independent and uniform on $\{1,\ldots,2n\}$. Independent trials can amplify success if the polynomials can be tested. | Randomness supplies neither a deterministic hitting list nor a method for computing the polynomials from arbitrary CNFs. |
| Use powers of two | Every assignment has a distinct weight. Each individual weight takes at most $n$ bits to write. The polynomial has degree up to $2^n-1$ and can contain $2^n$ terms. | A compact symbolic zero test with a polynomial worst-case bound could evade the cost of explicitly listing coefficients. |
| Count over the integers | Positive contributions cannot cancel, and $P_{F,w}(1)$ is the number of models. | Deciding whether that integer is positive is already SAT. An efficient way to compute or test it still needs a proof. |

**Why random isolation helps.** Fix all weights except $w_i$. The best support omitting $i$ has fixed weight $A$, and the best support containing $i$ has weight $B+w_i$ for fixed $B$. If both types occur, at most one choice of $w_i$ ties them. Two different globally minimum supports would differ in some coordinate where such a tie occurs. A union bound gives failure probability at most $n/(2n)$. [Mulmuley, U. Vazirani and V. Vazirani, *Matching is as Easy as Matrix Inversion*](https://people.eecs.berkeley.edu/~vazirani/pubs/matching.pdf).

**Existence of a short list.** For binary encodings of one fixed length $N$, rename active variable IDs densely so there are at most $N$ of them. A random vector of $N$ weights from $\{1,\ldots,2N\}$ isolates any particular satisfiable formula with probability at least $1/2$. A list of $N+1$ independent vectors misses a particular formula with probability at most $2^{-(N+1)}$. There are at most $2^N$ formulas of this length, so with probability at least $1/2$ the same list hits every satisfiable one. This proves existence of polynomial-size advice for the isolation step at each length. It gives no efficient uniform construction of that advice.

**Evaluation remains a separate problem.** At $t=1$, the polynomial gives the parity of the model count, regardless of the weights. Computing its entire coefficient vector would therefore solve parity-SAT. The candidate only needs to test if the polynomial is identically zero, which might admit a different approach. No efficient general test was established here. [Valiant and V. Vazirani, *NP is as easy as detecting unique solutions*](https://ics.uci.edu/~vazirani/ValVaz.pdf).

## Reproduce the example

Run Python 3 on [weight_isolation.py](weight_isolation.py). The standard-library script constructs the example, evaluates its assignments directly and prints the surviving exponents for both choices of weights. It also exhaustively checks the two-model construction on all 651 unordered assignment pairs for one through five variables, and the collision finder on all 363 weight vectors over $\{1,2,3\}$ at those sizes.
