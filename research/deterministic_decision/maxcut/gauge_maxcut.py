"""Exact signed-integer Max-Cut decision via parity switching and minimum cuts."""

from collections import deque
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Decision:
    meets_threshold: bool
    witness: tuple | None
    cover_size: int
    assignments_examined: int
    flow_calls: int


def _prepare(n, edges):
    combined = {}
    for u, v, weight in edges:
        if not all(type(value) is int for value in (u, v, weight)):
            raise ValueError("use integer vertex IDs and integer weights")
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError("vertex outside declared graph")
        if u != v:
            edge = min(u, v), max(u, v)
            combined[edge] = combined.get(edge, 0) + weight
    return [(u, v, w) for (u, v), w in sorted(combined.items()) if w]


def _switch(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w > 0))
        adj[v].append((u, w > 0))
    gauge = [-1] * n
    for root in range(n):
        if gauge[root] != -1:
            continue
        gauge[root] = 0
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v, parity in adj[u]:
                if gauge[v] == -1:
                    gauge[v] = gauge[u] ^ parity
                    queue.append(v)
    terms = [(u, v, abs(w), (gauge[u] ^ gauge[v]) ^ (w > 0)) for u, v, w in edges]
    return gauge, terms


def _cover(n, terms):
    # In switched coordinates, all pairs outside this cover prefer equality.
    uncovered = [(u, v) for u, v, _, parity in terms if parity]
    cover = []
    while uncovered:
        degrees = [0] * n
        for u, v in uncovered:
            degrees[u] += 1
            degrees[v] += 1
        chosen = max(range(n), key=degrees.__getitem__)
        cover.append(chosen)
        uncovered = [(u, v) for u, v in uncovered if u != chosen and v != chosen]
    return cover


def _source_side(residual, source, sink):
    # Edmonds-Karp, using positive residual capacity for all reachability tests.
    while True:
        parent = {source: source}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v, capacity in residual[u].items():
                if capacity > 0 and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            return parent.keys()
        path = []
        v = sink
        while v != source:
            u = parent[v]
            path.append((u, v))
            v = u
        delta = min(residual[u][v] for u, v in path)
        for u, v in path:
            residual[u][v] -= delta
            residual[v][u] += delta


def _best_completion(n, terms, pins):
    source, sink = n, n + 1
    residual = [{} for _ in range(n + 2)]

    def arc(u, v, w):
        residual[u][v] = residual[u].get(v, 0) + w
        residual[v].setdefault(u, 0)

    for u, v, w, parity in terms:
        if u in pins and v in pins:
            continue  # An additive constant for this assignment.
        if u not in pins and v not in pins:
            assert parity == 0
            arc(u, v, w)
            arc(v, u, w)
        else:
            fixed, free = (u, v) if u in pins else (v, u)
            preferred = pins[fixed] ^ parity
            if preferred == 0:
                arc(source, free, w)
            else:
                arc(free, sink, w)
    reachable = _source_side(residual, source, sink)
    return [pins[v] if v in pins else int(v not in reachable) for v in range(n)]


def cut_value(edges, bits):
    return sum(w for u, v, w in edges if bits[u] != bits[v])


def decide(n, edges, threshold):
    """Return YES with a cut witness, or NO, on an explicitly sized vertex set."""
    if type(n) is not int or n < 0 or type(threshold) is not int:
        raise ValueError("use a nonnegative vertex count and an integer threshold")
    graph = _prepare(n, edges)
    gauge, terms = _switch(n, graph)
    cover = _cover(n, terms)
    for candidate in ((0,) * n, tuple(gauge)):
        if cut_value(graph, candidate) >= threshold:
            return Decision(True, candidate, len(cover), 0, 0)
    upper = sum(max(0, w) for _, _, w in graph)
    if cover:
        # A conflicting non-tree edge plus its tree path is an inconsistent cycle.
        upper -= min(w for _, _, w, _ in terms)
    if not cover or threshold > upper:
        return Decision(False, None, len(cover), 0, 0)
    # Global complementation preserves all pair energies; fix one cover bit to zero.
    examined = 0
    for tail in product((0, 1), repeat=len(cover) - 1):
        pins = dict(zip(cover, (0, *tail), strict=True))
        y = _best_completion(n, terms, pins)
        candidate = tuple(bit ^ flip for bit, flip in zip(y, gauge, strict=True))
        examined += 1
        if cut_value(graph, candidate) >= threshold:
            return Decision(True, candidate, len(cover), examined, examined)
    return Decision(False, None, len(cover), examined, examined)
