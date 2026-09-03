import unittest
import pandas as pd
from backend.app.causal.estimators import TLearner
from backend.app.policy.economic_policy import EconomicPolicyOptimizer, DeterministicPolicyGovernor

class TestCausalAndPolicy(unittest.TestCase):
    def test_governor(self):
        gov = DeterministicPolicyGovernor()
        
        ctx_hard_decline = {"failure_code": "BANK_DECLINE", "amount_paise": 100000}
        res = gov.evaluate(ctx_hard_decline, 1) # RETRY_NOW
        self.assertEqual(res['status'], "REJECTED")
        
        ctx_insufficient = {"failure_code": "INSUFFICIENT_FUNDS", "amount_paise": 100000}
        res = gov.evaluate(ctx_insufficient, 1) # RETRY_NOW
        self.assertEqual(res['status'], "REJECTED")
        
        res = gov.evaluate(ctx_insufficient, 2) # RETRY_LATER
        self.assertEqual(res['status'], "APPROVED")
        
    def test_economic_policy(self):
        class DummyModel:
            def predict_all_effects(self, ctx):
                return {0: 0.0, 1: 0.05, 2: 0.20, 3: 0.0, 4: 0.0, 5: 0.0}
            def confidence(self, ctx, a):
                return "HIGH"
                
        opt = EconomicPolicyOptimizer(DummyModel())
        ctx = {"amount_paise": 10000} # 100 INR
        
        # Action 2: uplift 0.20 * 10000 = 2000. Cost = 100+20+10 = 130. Net = 1870
        # Action 1: uplift 0.05 * 10000 = 500. Cost = 100+50+20 = 170. Net = 330
        decision = opt.get_best_action(ctx)
        
        self.assertEqual(decision['recommended_action'], 2)
        self.assertGreater(decision['expected_incremental_value'], 1000)

if __name__ == '__main__':
    unittest.main()
