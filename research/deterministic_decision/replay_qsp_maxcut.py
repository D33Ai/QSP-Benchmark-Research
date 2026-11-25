"""Replay the three public Max-Cut benchmark graphs with a direct cut-value oracle."""

from itertools import combinations, product

from research.deterministic_decision.maxcut.gauge_maxcut import decide


def graphs():
    yield "path_13", 13, [(i, i + 1) for i in range(12)]
    yield "complete_14", 14, list(combinations(range(14), 2))
    yield "sparse_maxcut_12", 12, [
        (0, 5), (0, 9), (1, 6), (1, 8), (2, 7), (2, 9), (2, 10),
        (3, 9), (3, 10), (4, 5), (4, 10), (5, 8), (5, 10), (5, 11),
        (6, 7), (7, 10), (7, 11),
    ]


def cut_value(edges, bits):
    return sum(bits[u] != bits[v] for u, v in edges)


def main():
    print("instance,threshold,decision,cover_size,min_cut_calls")
    for name, n, edges in graphs():
        optimum = max(cut_value(edges, bits) for bits in product((0, 1), repeat=n))
        weighted = [(u, v, 1) for u, v in edges]
        for threshold in (optimum, optimum + 1):
            result = decide(n, weighted, threshold)
            if result.meets_threshold != (threshold == optimum):
                raise AssertionError((name, threshold, result))
            if result.meets_threshold:
                witness = result.witness
                if witness is None or cut_value(edges, witness) != optimum:
                    raise AssertionError((name, threshold, witness))
            print(f"{name},{threshold},{result.meets_threshold},{result.cover_size},{result.flow_calls}")


if __name__ == "__main__":
    main()
