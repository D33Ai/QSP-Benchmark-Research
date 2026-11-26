"""Carry-free PARTITION gadgets, a checked compression, and replay of the experiments.

Python 3.10+ standard library. Run "python study.py" for the full checks.
The recognizer has an explicit promise and rejects unsupported inputs.
"""
from collections import defaultdict
from itertools import combinations, product
from random import Random
import json

FANO = [tuple((i + d) % 7 for d in (0, 1, 3)) for i in range(7)]
CYCLE = [tuple((i + d) % 7 for d in (0, 1, 2)) for i in range(7)]
PAIRS = list(combinations(range(4), 2))


class Unsupported(ValueError):
    pass


def require(condition):
    if not condition:
        raise Unsupported("outside the implemented structural promise")


def generate(lines, width, seed=0):
    """Return integers alone. Shuffle the digit coordinates and the item order."""
    if width < 1 or width % 2 == 0:
        raise ValueError("width must be positive and odd")
    entries = defaultdict(list)
    next_row = len(lines)
    for row, vertices in enumerate(lines):
        entries[("slack", row)].append(row)
        for pos, point in enumerate(vertices):
            if width == 1:
                entries[("bit", point, 0)].append(row)
                continue
            terminals = []
            prev = None
            blocks = (width - 1) // 2
            for block in range(blocks):
                v = list(range(next_row, next_row + 4))
                next_row += 4
                for a, b in PAIRS:
                    entries[("internal", row, pos, block, a, b)] = [v[a],v[b]]
                if prev is not None:
                    entries[("bridge", row, pos, block)] = [prev, v.pop(0)]
                if block + 1 < blocks:
                    prev = v.pop()
                terminals.extend(v)
            entries[("output", row, pos)] = [terminals.pop(), row]
            assert len(terminals) == width
            for i, port in enumerate(terminals):
                entries[("bit", point, i)].append(port)
    rng = Random(seed)
    permutation = list(range(next_row))
    rng.shuffle(permutation)
    weights = [sum(1 << (3 * permutation[d]) for d in ds) for ds in entries.values()]
    rng.shuffle(weights)
    return weights


def digit_support(w):
    require(isinstance(w, int) and w > 0)
    result = []
    while w:
        low = w & -w
        pos = low.bit_length() - 1
        require(pos % 3 == 0)
        result.append(pos // 3)
        w -= low
    require(1 <= len(result) <= 3)
    return tuple(result)


def components(vertices, adjacent):
    unseen = set(vertices)
    while unseen:
        stack = [unseen.pop()]
        part = set(stack)
        while stack:
            node = stack.pop()
            fresh = adjacent[node] & unseen
            unseen.difference_update(fresh)
            part.update(fresh)
            stack.extend(fresh)
        yield part


def binary_tuple(index, size):
    return tuple((index >> i) & 1 for i in range(size))


def check_witness(weights, bits):
    return (len(bits) == len(weights) and all(b in (0, 1) for b in bits)
            and 2 * sum(w for w, b in zip(weights, bits) if b) == sum(weights))


def recognize(weights):
    """Recover constraints and XOR paths from the binary integers, with no labels."""
    columns = [digit_support(w) for w in weights]
    at = defaultdict(list)
    for j, ds in enumerate(columns):
        for d in ds:
            at[d].append(j)
    require(at and all(len(js) == 4 for js in at.values()))
    unaries = {j for j, ds in enumerate(columns) if len(ds) == 1}
    core = {columns[j][0] for j in unaries}
    require(len(core) == len(unaries) and len(core) > 0)
    inner = set(at) - core
    pairs = {}
    neighbors = {d: set() for d in inner}
    for j, ds in enumerate(columns):
        if len(ds) != 2:
            continue
        a, b = ds
        require(ds not in pairs and not (a in core and b in core))
        pairs[ds] = j
        if a in inner and b in inner:
            neighbors[a].add(b)
            neighbors[b].add(a)
    within = {a: {b for b in ns if len(ns & neighbors[b]) == 2}
              for a, ns in neighbors.items()}
    clique_sets = [tuple(sorted(block)) for block in components(inner, within)]
    clique_of = {d: block for block in clique_sets for d in block}
    for block in clique_sets:
        require(len(block) == 4 and all(set(block) - {d} == within[d] for d in block))
    paths = []
    port_inputs = {}
    for region in components(inner, neighbors):
        blocks = {clique_of[d] for d in region}
        block_neighbors = {b: set() for b in blocks}
        crossing = {}
        locations = {}
        input_ids = set()
        output_ids = set()
        for d in sorted(region):
            block = clique_of[d]
            external = [j for j in at[d] if not (len(columns[j]) == 2 and set(columns[j]) <= set(block))]
            require(len(external) == 1)
            j = external[0]
            locations[d] = j
            ds = columns[j]
            if len(ds) == 3:
                require(j not in input_ids)
                input_ids.add(j)
            elif len(ds) == 2:
                other = ds[0] if ds[1] == d else ds[1]
                if other in core:
                    output_ids.add(j)
                else:
                    other_block = clique_of[other]
                    edge = frozenset([block, other_block])
                    require(edge not in crossing or crossing[edge] == j)
                    crossing[edge] = j
                    block_neighbors[block].add(other_block)
            else:
                raise Unsupported("unexpected port")
        require(len(output_ids) == 1 and len(crossing) == len(blocks) - 1)
        require(all(len(ns) <= 2 for ns in block_neighbors.values()))
        start = next(b for b in blocks if len(block_neighbors[b]) <= 1)
        order = [start]
        previous = None
        while True:
            options = block_neighbors[order[-1]] - {previous}
            if not options:
                break
            previous = order[-1]
            order.append(next(iter(options)))
        require(len(order) == len(blocks))
        bridges = [crossing[frozenset((a,b))] for a,b in zip(order,order[1:])]
        output = next(iter(output_ids))
        port_inputs[output] = frozenset(input_ids)
        paths.append((order, bridges, locations))
    constraints = []
    slacks = []
    groups = []
    group_index = {}
    for d in sorted(core):
        js = at[d]
        slacks.append(next(j for j in js if j in unaries))
        group_ids = []
        for j in js:
            if j in unaries:
                continue
            support = frozenset([j]) if len(columns[j]) == 3 else port_inputs.get(j)
            require(support)
            if support not in group_index:
                group_index[support] = len(groups)
                groups.append(support)
            group_ids.append(group_index[support])
        require(len(set(group_ids)) == 3)
        constraints.append(tuple(group_ids))
    flat = [j for g in groups for j in g]
    require(set(flat) == {j for j,ds in enumerate(columns) if len(ds) == 3})
    return columns,pairs,paths,port_inputs,groups,constraints,slacks


def local_table():
    """Each 4-bit boundary pattern maps to all valid internal K4 edge masks."""
    out = {}
    for bound in product((0,1), repeat=4):
        candidates = []
        for e in product((0,1), repeat=6):
            if all(bound[i] + sum(b for b,uv in zip(e, PAIRS) if i in uv) == 2 for i in range(4)):
                candidates.append(e)
        out[bound] = candidates
    return out


LOCAL = local_table()


def fano_certificate(groups, lines):
    if len(groups) != 7 or len(lines) != 7:
        return False
    pairs = [tuple(sorted(p)) for line in lines for p in combinations(line,2)]
    return len(set(pairs)) == len(pairs) == 21


def image_basis(groups):
    """Return original column vectors spanning all attainable grouped parity values."""
    signatures = defaultdict(int)
    for i, support in enumerate(groups):
        for j in support:
            signatures[j] ^= 1 << i
    pivots = {}
    basis = []
    for j, signature in sorted(signatures.items()):
        remainder = signature
        while remainder:
            p = remainder.bit_length() - 1
            if p not in pivots:
                pivots[p] = remainder
                basis.append((j,signature))
                break
            remainder ^= pivots[p]
    return basis


def image_values(basis):
    """Enumerate attainable outputs and one choice of input columns for each."""
    for flags in product((0,1),repeat=len(basis)):
        output = 0
        selected = []
        for flag,(j,signature) in zip(flags,basis):
            if flag:
                output ^= signature
                selected.append(j)
        yield output,selected


def solve_recognized(weights):
    """A deterministic exact solver on the recognized layouts. Return a checked witness or NO."""
    cols,pairs,paths,outputs,groups,lines,slacks = recognize(weights)
    basis = image_basis(groups)
    if fano_certificate(groups,lines):
        return False, None, "pair-count certificate", len(basis)
    for output, selected in image_values(basis):
        colors = binary_tuple(output,len(groups))
        sums = [sum(colors[i] for i in line) for line in lines]
        if all(s in (1,2) for s in sums):
            break
    else:
        return False,None,"exhaustive grouped search",len(basis)
    x = [None]*len(cols)
    selected_set = set(selected)
    for j, ds in enumerate(cols):
        if len(ds) == 3:
            x[j] = int(j in selected_set)
    for j,support in outputs.items():
        x[j] = sum(x[i] for i in support) % 2
    for j,s in zip(slacks,sums):
        x[j] = 2-s
    for order,bridges,locations in paths:
        for idx,block in enumerate(order):
            if idx < len(bridges):
                right = bridges[idx]
                x[right] = sum(x[locations[d]] for d in block if locations[d] != right) % 2
            boundary = tuple(x[locations[d]] for d in block)
            selected = LOCAL[boundary][0]
            for (a,b), val in zip(PAIRS,selected):
                x[pairs[(block[a],block[b])]] = val
    assert check_witness(weights,x)
    return True,x,"integer witness",len(basis)


def exhaustive_integer(weights):
    sums = {0}
    for w in weights:
        sums |= {s+w for s in sums}
    target = sum(weights)
    return target % 2 == 0 and target//2 in sums


def valid_core(colors, lines):
    return all(len({colors[i] for i in line}) == 2 for line in lines)


def verify():
    assert all(bool(options) == (sum(p)%2 == 0) for p,options in LOCAL.items())
    for missing in range(7):
        subset = FANO[:missing]+FANO[missing+1:]
        colors = [c for c in product((0,1),repeat=7) if valid_core(c,subset)]
        assert colors and all({c[i] for c in colors} == {0,1} for i in range(7))
    macro_yes = {name:sum(valid_core(c,lines) for c in product((0,1),repeat=7))
                 for name,lines in [('Fano',FANO),('cycle',CYCLE)]}
    assert macro_yes['Fano']==0 and macro_yes['cycle']>0
    # Independently compare the parity-image enumerator with all raw assignments.
    rng = Random(641)
    for _ in range(200):
        variables = rng.randint(2,9)
        outputs = rng.randint(1,9)
        forms = [{j for j in range(variables) if rng.randrange(2)} for _ in range(outputs)]
        exact = {sum((sum(bits[j] for j in form) % 2) << i for i,form in enumerate(forms))
                 for bits in product((0,1), repeat=variables)}
        actual = set()
        for value,selected in image_values(image_basis(forms)):
            assert value == sum((len(set(selected) & form) % 2) << i for i,form in enumerate(forms))
            actual.add(value)
        assert actual == exact
    audit = []
    for width in (1,3,5,9,21,51):
        for name,lines,wanted in [('Fano',FANO,False),('cycle',CYCLE,True)]:
            for seed in (11,29,73):
                weights = generate(lines,width,seed)
                answer,bits,method,n = solve_recognized(weights)
                assert answer == wanted and n == 7
                if width == 1:
                    assert exhaustive_integer(weights) == answer
                if answer:
                    assert check_witness(weights,bits)
            audit.append(dict(width=width, family=name, weights=len(weights), digit_positions=1+(max(w.bit_length() for w in weights)-1)//3,
                              boundary_bits=7*width, ground_truth=wanted, method=method, shuffles=3))
    # The complete projections of global equations modulo 2 impose no boundary equations.
    # Check with a separate GF(2) Gaussian elimination on the integer-generated rows.
    parity_checks = []
    for width in (1,3,5,9):
        ws = generate(FANO,width,943)
        ds=[digit_support(w) for w in ws]
        k=sum(len(s)==3 for s in ds)
        elim_order=sorted(range(len(ws)),key=lambda j:len(ds[j])!=3)
        residuals=[0]*(1+max(d for s in ds for d in s))
        for col,j in enumerate(elim_order):
            for d in ds[j]: residuals[d]|=1<<col
        basis={}
        for row in residuals:
            while row:
                pivot=row.bit_length()-1
                if pivot not in basis:
                    basis[pivot]=row
                    break
                row^=basis[pivot]
        free_constraints=sum(p<k for p in basis)
        assert free_constraints==0
        parity_checks.append(dict(width=width,independent_restrictions_on_boundary=free_constraints))
    return dict(local_boundary_patterns=len(LOCAL),internal_patterns_per_boundary=64,
                core_colorings_checked_per_family=128,valid_macro_colorings=macro_yes,
                core_line_deletions_checked=7,random_parity_maps_compared=200,shuffled_numeric_instances=len(audit)*3,
                integer_equality_witnesses=sum(row["shuffles"] for row in audit if row["ground_truth"]),
                direct_small_integer_checks=6,parity_projection_checks=parity_checks, runs=audit)


if __name__ == "__main__":
    print(json.dumps(verify(),indent=2))
