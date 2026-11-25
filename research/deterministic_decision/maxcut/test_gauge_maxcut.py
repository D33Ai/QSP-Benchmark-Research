"""Independent oracles, exact inequalities, and a reproducible scaling experiment."""

import sys
import unittest
from itertools import combinations, product
from random import Random
from statistics import median
from time import perf_counter

from gauge_maxcut import decide


def value(edges, bits):
    return sum(weight * (bits[i] ^ bits[j]) for i, j, weight in edges)


def brute(n, edges):
    return max(value(edges, x) for x in product((0, 1), repeat=n))


def clique(n):
    return [(i, j, 1) for i, j in combinations(range(n), 2)]


class TestMaxCut(unittest.TestCase):
    def check_at_boundary(self, n, edges):
        target = brute(n, edges)
        yes = decide(n, edges, target)
        self.assertTrue(yes.meets_threshold)
        self.assertEqual(value(edges, yes.witness), target)
        no = decide(n, edges, target + 1)
        self.assertFalse(no.meets_threshold)
        self.assertIsNone(no.witness)

    def test_every_signed_graph_on_four_vertices(self):
        pairs = list(combinations(range(4), 2))
        for weights in product((-1, 0, 1), repeat=len(pairs)):
            self.check_at_boundary(4, [(*ij, w) for ij, w in zip(pairs, weights, strict=True)])

    def test_signed_multigraphs(self):
        rng = Random(33120)
        for _ in range(192):
            n = rng.randrange(1, 10)
            edges = [(rng.randrange(n), rng.randrange(n), rng.randint(-8, 8)) for _ in range(3 * n)]
            self.check_at_boundary(n, edges)

    def test_large_binary_weights(self):
        weights = [10**100 + i for i in range(10)]
        edges = [(*ij, w) for ij, w in zip(combinations(range(5), 2), weights, strict=True)]
        self.check_at_boundary(5, edges)

    def test_empty_graph_and_invalid_input(self):
        self.check_at_boundary(0, [])
        with self.assertRaises(ValueError):
            decide(3, [(0, 3, 1)], 1)
        with self.assertRaises(ValueError):
            decide(3, [(0, 2, 1.5)], 1)

    def test_bipartite_large_and_frustrated_cliques(self):
        edges = [(i, (i + 1) % 100, 7) for i in range(100)]
        result = decide(100, edges, 700)
        self.assertEqual(
            (value(edges, result.witness), result.cover_size, result.flow_calls), (700, 0, 0)
        )
        for n in range(5, 12):
            result = decide(n, clique(n), n * n // 4 + 1)
            self.assertFalse(result.meets_threshold)
            self.assertEqual(result.cover_size, n - 2)
            self.assertEqual(result.flow_calls, 2 ** (n - 3))


def run_benchmarks():
    print("vertices,edges,threshold,cover_size,flow_calls,median_ms")
    for n in (5, 7, 9, 11, 13, 15):
        graph = clique(n)
        threshold = n * n // 4 + 1
        observations = []
        for _ in range(5):
            start = perf_counter()
            result = decide(n, graph, threshold)
            observations.append(1000 * (perf_counter() - start))
        assert not result.meets_threshold
        assert result.flow_calls == 2 ** (n - 3)
        print(
            f"{n},{len(graph)},{threshold},{result.cover_size},"
            f"{result.flow_calls},{median(observations):.3f}"
        )


if __name__ == "__main__":
    if sys.argv[1:] == ["--benchmark"]:
        run_benchmarks()
    else:
        unittest.main()
