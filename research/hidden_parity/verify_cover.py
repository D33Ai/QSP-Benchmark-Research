"""Exhaustively check small flat covers and their private witnesses."""
from itertools import product
import json

LINES = tuple((i, (i + 1) % 7, (i + 3) % 7) for i in range(7))


def failures(colors):
    return [i for i, (a, b, c) in enumerate(LINES) if colors[a] == colors[b] == colors[c]]


def check(width):
    words = range(1 << width)
    size = 7 * width
    mask = len(words) - 1
    parity = [word.bit_count() % 2 for word in words]
    colors = list(product((0, 1), repeat=7))
    failed = {c: failures(c) for c in colors}
    patterns = set()
    for line_id, line in enumerate(LINES):
        for local in product(words, repeat=3):
            shade = parity[local[0]]
            if any(parity[w] != shade for w in local):
                continue
            extension = [1 - shade] * 7
            for p, w in zip(line, local):
                extension[p] = w
            assert failed[tuple(parity[w] for w in extension)] == [line_id]
            patterns.add((line_id, local))
    assert len(patterns) == 7 * (1 << (3 * width - 2))
    used = set()
    for assignment in range(1 << size):
        blocks = tuple((assignment >> (width * p)) & mask for p in range(7))
        matching = failed[tuple(parity[w] for w in blocks)]
        assert matching
        line_id = matching[0]
        key = (line_id, tuple(blocks[p] for p in LINES[line_id]))
        assert key in patterns
        used.add(key)
    assert used == patterns
    return dict(width=width, boundary_assignments=1 << size, local_patterns=len(patterns),
                private_extensions_checked=len(patterns), covered=True)


if __name__ == "__main__":
    print(json.dumps([check(1), check(3)], indent=2))
