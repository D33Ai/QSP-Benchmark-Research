"""Reproduce the parity cancellation in WEIGHT_ISOLATION.md using Python 3."""

from itertools import combinations, product


def colliding_assignments(weights):
    """Return two masks of equal weight, or None if all subset weights differ."""
    if any(type(weight) is not int or weight <= 0 for weight in weights):
        raise ValueError("weights must be positive integers")
    representative = {0: 0}
    for index, weight in enumerate(weights):
        for total, mask in list(representative.items()):
            next_total = total + weight
            next_mask = mask | (1 << index)
            if next_total in representative:
                return representative[next_total], next_mask
            representative[next_total] = next_mask
    return None


def two_model_cnf(size, first, second):
    """Pin agreeing bits and link every other differing bit to one pivot."""
    difference = first ^ second
    if not difference or min(first, second) < 0 or max(first, second) >= 1 << size:
        raise ValueError("expected two distinct masks on the given variables")
    pivot = (difference & -difference).bit_length()  # one-based DIMACS id
    clauses = []
    for variable in range(1, size + 1):
        bit = 1 << (variable - 1)
        if variable == pivot:
            continue
        if not difference & bit:
            clauses.append((variable if first & bit else -variable,))
        elif bool(first & bit) == bool(first & (1 << (pivot - 1))):
            clauses.extend(((-pivot, variable), (pivot, -variable)))
        else:
            clauses.extend(((pivot, variable), (-pivot, -variable)))
    return clauses


def models(size, clauses):
    for assignment in range(1 << size):
        if all(
            any(bool(assignment & (1 << (abs(lit) - 1))) == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            yield assignment


def weight_of(mask, weights):
    return sum(weight for i, weight in enumerate(weights) if mask & (1 << i))


def odd_exponents(assignments, weights):
    support = set()
    for assignment in assignments:
        support.symmetric_difference_update([weight_of(assignment, weights)])
    return sorted(support)


def self_test():
    pair_count = vector_count = 0
    for size in range(1, 6):
        weightings = [(1,) * size]
        weightings.extend(tuple(2 if i == j else 1 for i in range(size)) for j in range(size))
        for first, second in combinations(range(1 << size), 2):
            clauses = two_model_cnf(size, first, second)
            assert list(models(size, clauses)) == [first, second]
            assert any(odd_exponents((first, second), w) for w in weightings)
            pair_count += 1
        for weights in product(range(1, 4), repeat=size):
            distinct_sums = {weight_of(mask, weights) for mask in range(1 << size)}
            pair = colliding_assignments(weights)
            assert (pair is None) == (len(distinct_sums) == 1 << size)
            if pair is not None:
                assert pair[0] != pair[1]
                assert weight_of(pair[0], weights) == weight_of(pair[1], weights)
            vector_count += 1
    xor_pairs = ((1, 2), (-1, -2), (3, 4), (-3, -4))
    four_models = list(models(4, xor_pairs))
    assert len(four_models) == 4
    for boosted in (None, 0, 1, 2, 3):
        weights = tuple(2 if i == boosted else 1 for i in range(4))
        assert not odd_exponents(four_models, weights)
    return pair_count, vector_count


if __name__ == "__main__":
    pair_count, vector_count = self_test()
    print(f"Verified all {pair_count} model pairs and {vector_count} weight vectors.")
    fixed_weights = (1, 2, 3)
    first, second = colliding_assignments(fixed_weights)
    example = two_model_cnf(len(fixed_weights), first, second)
    satisfying = list(models(len(fixed_weights), example))
    print("CNF clauses (signed variable IDs):", example)
    for assignment in satisfying:
        bits = tuple((assignment >> i) & 1 for i in range(len(fixed_weights)))
        print(f"Model {bits}, weight {weight_of(assignment, fixed_weights)}")
    print("Odd exponents under (1, 2, 3):", odd_exponents(satisfying, fixed_weights))
    print("Odd exponents under (1, 2, 4):", odd_exponents(satisfying, (1, 2, 4)))
