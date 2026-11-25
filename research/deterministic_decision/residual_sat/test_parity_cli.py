"""Check the DIMACS command with known YES and NO answers on cubic graphs."""

import json
import subprocess
import sys
import tempfile
import unittest
from itertools import product
from pathlib import Path

SOLVER = Path(__file__).with_name("residual_sat.py")


def prism_cnf(rim_size, charged):
    edges = []
    for rim in (0, rim_size):
        edges.extend((rim + i, rim + (i + 1) % rim_size) for i in range(rim_size))
    edges.extend((i, rim_size + i) for i in range(rim_size))
    clauses = []
    for vertex in range(2 * rim_size):
        incident = [var for var, edge in enumerate(edges, start=1) if vertex in edge]
        for bits in product((0, 1), repeat=3):
            if sum(bits) % 2 != int(vertex in charged):
                # This clause excludes precisely one assignment of the incident edge bits.
                clauses.append(
                    tuple(-v if bit else v for v, bit in zip(incident, bits, strict=True))
                )
    return len(edges), clauses


class PrismParityTests(unittest.TestCase):
    def test_cli_decisions_and_witnesses(self):
        # Summing vertex parities counts each edge twice. Conversely, any even set of
        # charged vertices is realized by pairing them and toggling paths in the prism.
        with tempfile.TemporaryDirectory() as folder:
            cnf = Path(folder) / "prism.cnf"
            for size in (3, 5, 7, 9, 12):
                for charged in ((), (0,), (0, size), (0, 1, size)):
                    with self.subTest(rim_size=size, charged=charged):
                        variables, clauses = prism_cnf(size, charged)
                        lines = [f"p cnf {variables} {len(clauses)}"]
                        lines.extend(" ".join(map(str, clause)) + " 0" for clause in clauses)
                        cnf.write_text("\n".join(lines) + "\n", encoding="ascii")
                        output = subprocess.check_output([sys.executable, str(SOLVER), str(cnf)])
                        result = json.loads(output)
                        self.assertEqual(result["satisfiable"], len(charged) % 2 == 0)
                        if result["satisfiable"]:
                            witness = set(result["true_variables"])
                            self.assertTrue(
                                all(
                                    any((abs(v) in witness) == (v > 0) for v in clause)
                                    for clause in clauses
                                )
                            )
                        else:
                            self.assertIsNone(result["true_variables"])
