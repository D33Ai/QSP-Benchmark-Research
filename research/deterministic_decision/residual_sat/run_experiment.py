"""Generate reproducible, machine-independent operation counts and truth-table checks."""

from __future__ import annotations

import argparse
import json
import random
from itertools import product
from pathlib import Path

from residual_sat import compile_3cnf

SEED = 20261125


def evaluate(clauses, true_variables):
    """Direct disjunction/conjunction evaluation of the original, unsimplified input."""
    return all(any((abs(v) in true_variables) == (v > 0) for v in c) for c in clauses)


def verify_case(clauses, variables, order=None):
    diagram = compile_3cnf(clauses, order)
    any_solution = False
    checked = 0
    for bits in product((False, True), repeat=len(variables)):
        assignment = {v for v, b in zip(variables, bits, strict=True) if b}
        expected = evaluate(clauses, assignment)
        if expected != diagram.accepts(assignment):
            raise AssertionError((clauses, order, assignment))
        any_solution |= expected
        checked += 1
    witness = diagram.witness()
    if (
        diagram.satisfiable != any_solution
        or (witness is not None) != any_solution
        or (witness is not None and not evaluate(clauses, witness))
    ):
        raise AssertionError(("decision/witness mismatch", clauses, order, witness))
    return any_solution, checked


def oracle_corpus():
    rng = random.Random(SEED)
    groups = {}

    def record(group, clauses, variables):
        row = groups.setdefault(group, dict(formulas=0, sat=0, unsat=0, assignments_checked=0))
        row["formulas"] += 1
        for order in (None, tuple(reversed(variables))):
            answer, checked = verify_case(clauses, variables, order)
            row["assignments_checked"] += checked
        row["sat" if answer else "unsat"] += 1

    # Each signed three-literal clause over these variables excludes one assignment.
    variables = (1, 2, 3)
    possible = [
        tuple(v * sign for v, sign in zip(variables, signs, strict=True))
        for signs in product((-1, 1), repeat=3)
    ]
    for subset in range(1 << len(possible)):
        record(
            "all_subsets_of_eight_distinct_3_variable_3_clauses",
            [c for i, c in enumerate(possible) if subset & (1 << i)],
            variables,
        )

    for n in (4, 6, 8):
        variables = tuple(range(1, n + 1))
        for _ in range(40):
            clauses = [
                tuple(v * rng.choice((-1, 1)) for v in rng.sample(variables, 3))
                for _ in range(rng.randint(3 * n, 7 * n))
            ]
            record(f"seeded_3_sat_n{n}", clauses, variables)

    for clauses in (
        [],
        [()],
        [(1,), (-1,)],
        [(1, -1), (2, 2)],
        [(1, 2), (1,)],
        [(9, -3, 1), (1, -9), (3, -1)],
        [(1,), (1, 1), (1, 1, 1)],
    ):
        record(
            "degenerate_and_mixed_width",
            clauses,
            tuple(sorted({abs(v) for c in clauses for v in c})),
        )
    return groups


def grid_edges(side):
    edges = []
    for row in range(side):
        for col in range(side):
            vertex = 1 + row * side + col
            if col + 1 < side:
                edges.append((vertex, vertex + 1))
            if row + 1 < side:
                edges.append((vertex, vertex + side))
    return edges


def grid_3cnf(side):
    selector = side * side + 1
    return [
        clause for a, b in grid_edges(side) for clause in ((-selector, a, b), (selector, -a, -b))
    ]


def grid_compilations():
    rows = []
    for side in range(2, 7):
        clauses = grid_3cnf(side)
        selector = side * side + 1
        numeric = (selector, *range(1, selector))
        for name, order in (("selector_first_row_major", numeric), ("greedy_boundary", None)):
            diagram = compile_3cnf(clauses, order)
            witness = diagram.witness()
            if witness is None or not evaluate(clauses, witness):
                raise AssertionError(("grid decision/witness mismatch", side, name))
            rows.append(
                {
                    "side": side,
                    "variables": selector,
                    "clauses": len(clauses),
                    "order": name,
                    "satisfiable": diagram.satisfiable,
                    "nonterminal_nodes": len(diagram.nodes) - 2,
                    "max_nodes_at_one_variable": max(diagram.nodes_per_variable.values()),
                    "expanded_residuals": diagram.expanded_residuals,
                }
            )
    return rows


def cut_matching(edges, prefix):
    neighbors = {}
    crossing = []
    for a, b in edges:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
        if (a in prefix) != (b in prefix):
            crossing.append((a, b) if a in prefix else (b, a))
    blocked = set()
    matching = []
    for a, b in crossing:
        if a not in blocked and b not in blocked:
            matching.append((a, b))
            blocked.update((a, b))
            blocked.update(neighbors[a])
            blocked.update(neighbors[b])
    return len(crossing), matching


def matching_checks():
    rows = []
    for side in (4, 8, 16, 32, 64):
        rng = random.Random(SEED + side)
        numeric = list(range(1, side * side + 1))
        shuffled = numeric.copy()
        rng.shuffle(shuffled)
        checkerboard = sorted(numeric, key=lambda v: (sum(divmod(v - 1, side)) % 2, v))
        edges = grid_edges(side)
        for name, order in (
            ("row_major", numeric),
            ("checkerboard", checkerboard),
            ("seeded_shuffle", shuffled),
        ):
            prefix = set(order[: len(order) // 2])
            crossing, matching = cut_matching(edges, prefix)
            endpoints = {v for pair in matching for v in pair}
            induced = {(a, b) for a, b in edges if a in endpoints and b in endpoints}
            if (
                induced != {tuple(sorted(pair)) for pair in matching}
                or len(endpoints) != 2 * len(matching)
                or len(matching) * 80 < side
            ):
                raise AssertionError(("induced matching certificate failed", side, name))
            # Check signatures against the actual 3-CNF for the smaller grids.
            signature_size = min(7, len(matching)) if side <= 16 else 0
            if signature_size:
                clauses = grid_3cnf(side)
                universe = set(numeric) | {side * side + 1}
                observed = set()
                for bits in product((False, True), repeat=signature_size):
                    left_false = {
                        a
                        for bit, (a, _) in zip(bits, matching[:signature_size], strict=True)
                        if bit
                    }
                    signature = tuple(
                        evaluate(clauses, universe - left_false - {b})
                        for _, b in matching[:signature_size]
                    )
                    observed.add(signature)
                if len(observed) != 2**signature_size:
                    raise AssertionError(("inequivalent prefix check failed", side, name))
            rows.append(
                {
                    "side": side,
                    "prefix_order": name,
                    "crossing_edges": crossing,
                    "induced_matching_edges": len(matching),
                    "log2_distinct_residuals_lower_bound": len(matching),
                    "distinct_signatures_checked_by_truth_evaluation": (
                        2**signature_size if signature_size else 0
                    ),
                }
            )
    return rows


def run():
    return {
        "seed": SEED,
        "orders_per_oracle_formula": 2,
        "oracle_checks": oracle_corpus(),
        "grid_compilations": grid_compilations(),
        "cut_certificates": matching_checks(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = json.dumps(run(), indent=2) + "\n"
    if args.json:
        args.json.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
