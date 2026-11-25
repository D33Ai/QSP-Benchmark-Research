"""A deterministic exact 3-CNF decision experiment using reduced ordered BDDs."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

Clause = tuple[int, ...]
Formula = tuple[Clause, ...]
TRUE: Formula = ()
FALSE: Formula = ((),)


def normalize(clauses: Iterable[Iterable[int]]) -> Formula:
    """Validate the full input, remove tautologies, duplicates and subsumed clauses."""
    unique = set()
    for clause in clauses:
        values = tuple(clause)
        if len(values) > 3 or any(type(v) is not int or v == 0 for v in values):
            raise ValueError("a 3-CNF clause must contain at most three nonzero integers")
        literals = set(values)
        if not any(-v in literals for v in literals):
            unique.add(tuple(sorted(literals)))
    if () in unique:
        return FALSE
    return tuple(
        sorted(
            clause
            for clause in unique
            if not any(
                part in unique for n in range(1, len(clause)) for part in combinations(clause, n)
            )
        )
    )


def cofactor(formula: Formula, true_literal: int) -> Formula:
    """Substitute a signed literal as true."""
    return normalize(
        (v for v in clause if v != -true_literal)
        for clause in formula
        if true_literal not in clause
    )


def boundary_order(formula: Formula) -> tuple[int, ...]:
    """Greedily minimize the next processed-to-unprocessed vertex boundary."""
    adjacent: dict[int, set[int]] = {}
    for clause in formula:
        variables = {abs(v) for v in clause}
        for var in variables:
            adjacent.setdefault(var, set()).update(variables - {var})
    remaining = set(adjacent)
    degree = {v: len(neighbors) for v, neighbors in adjacent.items()}
    frontier: set[int] = set()
    order = []

    def key(v: int) -> tuple[int, int, int, int]:
        retired = sum(u in frontier and degree[u] == 1 for u in adjacent[v])
        return (int(degree[v] > 0) - retired, degree[v] - len(adjacent[v]), degree[v], v)

    while remaining:
        v = min(remaining, key=key)
        remaining.remove(v)
        order.append(v)
        if degree[v]:
            frontier.add(v)
        for u in adjacent[v]:
            degree[u] -= 1
            if not degree[u]:
                frontier.discard(u)
    return tuple(order)


@dataclass
class Diagram:
    """Nodes 0 and 1 are terminals. A positive root ID certifies satisfiability."""

    root: int
    nodes: list[tuple[int, int, int] | None]
    order: tuple[int, ...]
    expanded_residuals: int
    nodes_per_variable: dict[int, int]

    @property
    def satisfiable(self) -> bool:
        return self.root != 0

    def accepts(self, true_variables: set[int]) -> bool:
        current = self.root
        while current > 1:
            node = self.nodes[current]
            assert node is not None
            var, low, high = node
            current = high if var in true_variables else low
        return current == 1

    def witness(self) -> set[int] | None:
        """Return true variables of a satisfying assignment, with all others false."""
        if not self.satisfiable:
            return None
        selected = set()
        current = self.root
        while current > 1:
            node = self.nodes[current]
            assert node is not None
            var, low, high = node
            if low == 0:
                selected.add(var)
                current = high
            else:
                current = low
        return selected


def compile_3cnf(clauses: Iterable[Iterable[int]], order: Sequence[int] | None = None) -> Diagram:
    """Compile the full Boolean function exactly, with an optional fixed variable order."""
    formula = normalize(clauses)
    variables = {abs(v) for clause in formula for v in clause}
    chosen = boundary_order(formula) if order is None else tuple(order)
    rank = {v: i for i, v in enumerate(chosen)}
    if (
        any(type(v) is not int or v < 1 for v in chosen)
        or len(rank) != len(chosen)
        or not variables.issubset(rank)
    ):
        raise ValueError("order must list distinct positive IDs and cover all active variables")

    memo = {FALSE: 0, TRUE: 1}
    nodes: list[tuple[int, int, int] | None] = [None, None]
    intern: dict[tuple[int, int, int], int] = {}
    widths: dict[int, int] = {}
    # Each frame is a residual and, on its second visit, its two children.
    pending: list[tuple[Formula, tuple[int, Formula, Formula] | None]] = [(formula, None)]
    while pending:
        residual, children = pending.pop()
        if residual in memo:
            continue
        if children is None:
            var = min((abs(v) for clause in residual for v in clause), key=rank.__getitem__)
            low = cofactor(residual, -var)
            high = cofactor(residual, var)
            pending.append((residual, (var, low, high)))
            pending.append((high, None))
            pending.append((low, None))
            continue
        var, low, high = children
        low_id, high_id = memo[low], memo[high]
        if low_id == high_id:
            memo[residual] = low_id
            continue
        node = (var, low_id, high_id)
        if node not in intern:
            intern[node] = len(nodes)
            nodes.append(node)
            widths[var] = widths.get(var, 0) + 1
        memo[residual] = intern[node]
    return Diagram(memo[formula], nodes, chosen, len(memo) - 2, widths)


def decimal_integer(field: str) -> int:
    """Parse a signed ASCII decimal token without a runtime digit-length ceiling."""
    sign = -1 if field.startswith("-") else 1
    digits = field[1:] if field.startswith(("+", "-")) else field
    if not digits.isascii() or not digits.isdigit():
        raise ValueError("invalid signed decimal integer in DIMACS input")
    value = 0
    for start in range(0, len(digits), 9):
        chunk = digits[start : start + 9]
        value = value * 10 ** len(chunk) + int(chunk)
    return sign * value


def read_dimacs(text: str) -> list[Clause]:
    """Read DIMACS with clauses of at most three literals, including empty clauses."""
    header = None
    result = []
    clause: list[int] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        parts = line.split()
        if parts[0] == "p":
            if header is not None or len(parts) != 4 or parts[1] != "cnf":
                raise ValueError("expected one p cnf <variables> <clauses> header")
            header = (decimal_integer(parts[2]), decimal_integer(parts[3]))
            if min(header) < 0:
                raise ValueError("negative DIMACS header count")
            continue
        if header is None:
            raise ValueError("missing DIMACS header")
        for field in parts:
            literal = decimal_integer(field)
            if literal == 0:
                result.append(tuple(clause))
                clause = []
            elif abs(literal) > header[0] or len(clause) == 3:
                raise ValueError("literal or clause width exceeds the declared 3-CNF domain")
            else:
                clause.append(literal)
    if header is None or clause or len(result) != header[1]:
        raise ValueError("incomplete DIMACS input or clause count mismatch")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dimacs", type=Path)
    args = parser.parse_args()
    diagram = compile_3cnf(read_dimacs(args.dimacs.read_text(encoding="ascii")))
    witness = diagram.witness()
    # This dedicated CLI may need to print full-width variable IDs in its JSON.
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    print(
        json.dumps(
            {
                "satisfiable": diagram.satisfiable,
                "true_variables": sorted(witness) if witness is not None else None,
                "nonterminal_nodes": len(diagram.nodes) - 2,
                "expanded_residuals": diagram.expanded_residuals,
            },
            indent=2,
        )
    )
