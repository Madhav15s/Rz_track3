import unittest
import pandas as pd
from scripts.train_and_evaluate import evaluate_policy_on_oracle

class TestLeakage(unittest.TestCase):
    def test_evaluation_leakage(self):
        # Create dummy dataframes
        df_features = pd.DataFrame([
            {'case_id': 'case_1', 'amount_paise': 1000, 'failure_code': 'BANK_TIMEOUT'}
        ])
        
        df_oracle = pd.DataFrame([
            {'case_id': 'case_1', 'y_0': 0, 'y_1': 1, 'y_2': 0, 'y_3': 0, 'y_4': 0, 'y_5': 0}
        ])
        
        # Policy that crashes if oracle data leaks
        def strict_policy_fn(ctx):
            for i in range(6):
                if f'y_{i}' in ctx:
                    raise ValueError(f"LEAKAGE DETECTED: y_{i} in context!")
            return 1 # return action 1
            
        metrics = evaluate_policy_on_oracle(df_features, df_oracle, strict_policy_fn)
        self.assertEqual(metrics['interventions'], 1)
        self.assertEqual(metrics['incremental_revenue'], 1000) # (1 - 0) * 1000

if __name__ == '__main__':
    unittest.main()
