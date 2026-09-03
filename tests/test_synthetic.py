import unittest
from simulator.generators.synthetic_data import SyntheticWorldGenerator

class TestSyntheticWorld(unittest.TestCase):
    def test_generation(self):
        gen = SyntheticWorldGenerator(seed=123)
        customers = gen.generate_customers(100)
        cases, outcomes = gen.generate_cases_and_outcomes(customers)
        
        self.assertEqual(len(customers), 100)
        self.assertEqual(len(cases), 100)
        self.assertEqual(len(outcomes), 100)
        
        # Ensure potential outcomes are binary 0 or 1
        for out in outcomes:
            self.assertIn(out.y_0, [0, 1])
            self.assertIn(out.y_1, [0, 1])
            self.assertIn(out.y_2, [0, 1])
            self.assertIn(out.y_3, [0, 1])
            self.assertIn(out.y_4, [0, 1])
            self.assertIn(out.y_5, [0, 1])

if __name__ == '__main__':
    unittest.main()
