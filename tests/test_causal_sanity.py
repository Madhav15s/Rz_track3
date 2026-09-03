import unittest
import pandas as pd
import numpy as np
from backend.app.causal.estimators import TLearner
from backend.app.policy.economic_policy import EconomicPolicyOptimizer

class TestCausalSanity(unittest.TestCase):
    def setUp(self):
        self.context = {
            'case_id': 'test_case',
            'amount_paise': 100000,
            'time_since_failure_minutes': 10,
            'historical_payment_success_rate': 0.8,
            'engagement_score': 0.9,
            'payment_method': 'card',
            'failure_code': 'BANK_TIMEOUT',
            'customer_value_band': 'high'
        }

    def _make_dummy_dataset(self, num_samples=100, y_probs=None):
        """Helper to create fake data forcing specific outcomes"""
        if y_probs is None:
            y_probs = {a: 0.5 for a in range(6)}
            
        rows = []
        treatments = []
        outcomes = []
        for i in range(num_samples):
            cid = f'c_{i}'
            rows.append({
                'case_id': cid, 'amount_paise': 100000, 'time_since_failure_minutes': 10,
                'historical_payment_success_rate': 0.8, 'engagement_score': 0.9,
                'payment_method': 'card', 'failure_code': 'BANK_TIMEOUT', 'customer_value_band': 'high'
            })
            # Assign treatment deterministically round-robin
            a = i % 6
            treatments.append({'case_id': cid, 'assigned_action': a, 'propensity': 1/6.0})
            
            y_val = 1 if np.random.rand() < y_probs[a] else 0
            outcomes.append({'case_id': cid, 'assigned_action': a, 'y_observed': y_val})
            
        return pd.DataFrame(rows), pd.DataFrame(treatments), pd.DataFrame(outcomes)

    def test_a_zero_treatment_effects(self):
        # All actions have exactly 50% recovery probability -> 0 uplift
        y_probs = {0: 0.5, 1: 0.5, 2: 0.5, 3: 0.5, 4: 0.5, 5: 0.5}
        df_feat, df_treat, df_out = self._make_dummy_dataset(600, y_probs)
        
        model = TLearner()
        model.fit(df_feat, df_treat, df_out)
        
        effects = model.predict_all_effects(self.context)
        for a in range(1, 6):
            self.assertAlmostEqual(effects[a], 0.0, delta=0.20) # Within noise margin

    def test_b_large_positive_uplift(self):
        # Action 2 is amazing
        y_probs = {0: 0.2, 1: 0.2, 2: 0.9, 3: 0.2, 4: 0.2, 5: 0.2}
        df_feat, df_treat, df_out = self._make_dummy_dataset(600, y_probs)
        
        model = TLearner()
        model.fit(df_feat, df_treat, df_out)
        opt = EconomicPolicyOptimizer(model)
        
        action = opt.get_best_action(self.context)['recommended_action']
        self.assertEqual(action, 2)

    def test_c_negative_uplift(self):
        # Action 1 is terrible
        y_probs = {0: 0.5, 1: 0.1, 2: 0.5, 3: 0.5, 4: 0.5, 5: 0.5}
        df_feat, df_treat, df_out = self._make_dummy_dataset(600, y_probs)
        
        model = TLearner()
        model.fit(df_feat, df_treat, df_out)
        opt = EconomicPolicyOptimizer(model)
        
        action = opt.get_best_action(self.context)['recommended_action']
        self.assertNotEqual(action, 1)

    def test_d_high_natural_recovery(self):
        # Y_0 is 95%.
        y_probs = {0: 0.95, 1: 0.95, 2: 0.95, 3: 0.95, 4: 0.95, 5: 0.95}
        df_feat, df_treat, df_out = self._make_dummy_dataset(3000, y_probs)
        
        for a in range(6):
            df_out.loc[a, 'y_observed'] = 0
            df_out.loc[a+6, 'y_observed'] = 1
            
        model = TLearner()
        model.fit(df_feat, df_treat, df_out)
        
        # Make amount very small so cost outweighs noise
        ctx_expensive = self.context.copy()
        ctx_expensive['amount_paise'] = 1000  # 10 INR
        
        # Override catalog temporarily in memory for the test to ensure NO_ACTION is picked 
        # (even if random noise gives +1% uplift, 1000 * 0.01 = 10, but costs are 160)
        opt = EconomicPolicyOptimizer(model)
        action = opt.get_best_action(ctx_expensive)['recommended_action']
        self.assertEqual(action, 0)
        
    def test_e_heterogeneous_effects(self):
        # Action 1 works for 'high' value band, Action 2 works for 'low' value band
        df_feat, df_treat, df_out = self._make_dummy_dataset(2400)
        # Modify half to be low
        df_feat.loc[1200:, 'customer_value_band'] = 'low'
        
        for i in range(2400):
            band = df_feat.loc[i, 'customer_value_band']
            a = df_treat.loc[i, 'assigned_action']
            
            # Control is 10%
            prob = 0.1
            
            if band == 'high' and a == 1:
                prob = 0.9
            elif band == 'low' and a == 2:
                prob = 0.9
                
            df_out.loc[i, 'y_observed'] = 1 if np.random.rand() < prob else 0
            
        # Add deterministic bounds
        for a in range(6):
            df_out.loc[a, 'y_observed'] = 0
            df_out.loc[a+6, 'y_observed'] = 1
            df_out.loc[1200+a, 'y_observed'] = 0
            df_out.loc[1200+a+6, 'y_observed'] = 1
            
        model = TLearner()
        model.fit(df_feat, df_treat, df_out)
        
        opt = EconomicPolicyOptimizer(model)
        
        ctx_high = self.context.copy()
        ctx_high['customer_value_band'] = 'high'
        a_high = opt.get_best_action(ctx_high)['recommended_action']
        
        ctx_low = self.context.copy()
        ctx_low['customer_value_band'] = 'low'
        a_low = opt.get_best_action(ctx_low)['recommended_action']
        
        self.assertEqual(a_high, 1)
        self.assertEqual(a_low, 2)
if __name__ == '__main__':
    np.random.seed(42)
    unittest.main()
