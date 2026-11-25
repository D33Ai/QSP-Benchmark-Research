import unittest
from itertools import product

from residual_sat import compile_3cnf, read_dimacs
from run_experiment import grid_3cnf, verify_case


class ResidualSATTests(unittest.TestCase):
    def test_constants_and_empty_witness(self):
        self.assertEqual(compile_3cnf([]).witness(), set())
        self.assertIsNone(compile_3cnf([()]).witness())
        self.assertEqual(compile_3cnf([(-8,)]).witness(), set())

    def test_semantic_reduction_of_variable(self):
        diagram = compile_3cnf([(1, 2), (-1, 2)], order=(1, 2))
        self.assertEqual(diagram.nodes[diagram.root], (2, 0, 1))
        self.assertEqual(len(diagram.nodes) - 2, 1)

    def test_sparse_identifiers_and_irrelevant_variables(self):
        large = 1 << 80
        diagram = compile_3cnf([(large,), (-large, 3), (-17, 17)], order=(4, large, 3))
        self.assertEqual(diagram.witness(), {3, large})

    def test_dimacs_header_and_multiline_clauses(self):
        clauses = read_dimacs("c example\np cnf 9 2\n1 -2\n3 0 -9 0\n")
        self.assertEqual(clauses, [(1, -2, 3), (-9,)])
        self.assertEqual(read_dimacs("p cnf 0 1\n0"), [()])
        self.assertEqual(read_dimacs("p cnf 9 0\n"), [])

    def test_unbounded_sparse_decimal_identifier(self):
        digits = "1" + "0" * 4500
        clauses = read_dimacs(f"p cnf {digits} 1\n{digits} 0")
        self.assertEqual(compile_3cnf(clauses).witness(), {10**4500})

    def test_bad_dimacs_input(self):
        for text in (
            "1 0",
            "p cnf -1 0",
            "p cnf 3 1\n1",
            "p cnf 3 1\n4 0",
            "p cnf 4 1\n1 2 3 -4 0",
            "p cnf 3 1\n",
            "p cnf 2 0\np cnf 3 0",
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                read_dimacs(text)

    def test_invalid_formulas_and_orders(self):
        # An empty clause is valid, but does not hide invalid input following it.
        for clauses in ([(), (0,)], [(True,)], [(0,)], [(1, 2, 3, 4)]):
            with self.subTest(clauses=clauses), self.assertRaises(ValueError):
                compile_3cnf(clauses)
        for order in ((), (2,), (1, 1), (True,), (1, -2)):
            with self.subTest(order=order), self.assertRaises(ValueError):
                compile_3cnf([(1,)], order)

    def test_exact_three_literal_grid_under_different_orders(self):
        clauses = grid_3cnf(2)
        for order in ((1, 2, 3, 4, 5), (5, 1, 2, 3, 4), (3, 1, 5, 2, 4)):
            self.assertEqual(verify_case(clauses, (1, 2, 3, 4, 5), order), (True, 32))

    def test_all_subsets_of_two_sparse_variable_clauses(self):
        variables = (17, 42)
        clauses = [(), (17,), (-17,), (42,), (-42,), *product((17, -17), (42, -42))]
        for subset in range(1 << len(clauses)):
            formula = [c for i, c in enumerate(clauses) if subset & (1 << i)]
            for order in (None, variables, variables[::-1]):
                verify_case(formula, variables, order)


if __name__ == "__main__":
    unittest.main()
