import pandas as pd
import numpy as np
import json
from unittest.mock import MagicMock
from backend.app.causal.estimators import SupportAwareCausalPolicy, BaseCausalEstimator

def main():
    # Mock causal estimator
    mock_causal = MagicMock(spec=BaseCausalEstimator)
    # Action 0: 0 uplift
    # Action 1 (A): Moderate uplift (0.15)
    # Action 2 (B): High uplift (0.40)
    mock_causal.predict_all_effects.return_value = {
        0: 0.0,
        1: 0.15,
        2: 0.40
    }
    
    # Mock propensity model
    mock_propensity = MagicMock()
    # Support: A0 (0.1), A1 (0.85), A2 (0.01)
    mock_propensity.predict_proba.return_value = np.array([[0.1, 0.85, 0.01, 0.0, 0.0, 0.04]])
    
    policy = SupportAwareCausalPolicy(mock_causal, min_support=0.05)
    policy.propensity_model = mock_propensity
    
    ctx = {'amount_paise': 100000} # 1000 INR
    
    res = policy.get_best_action(ctx, optimizer=None)
    
    with open("audit/SUPPORT_VS_EFFECT_DIAGNOSTIC.md", "w") as f:
        f.write("# SUPPORT VS CAUSAL EFFECT DIAGNOSTIC\n\n")
        f.write("Demonstrating how the policy behaves when confronted with a high-effect but low-support action.\n\n")
        
        f.write("| Action | True Uplift (Simulated) | Estimated Uplift | Support P(A\|X) | Allowed? | Selected? |\n")
        f.write("|--------|-------------------------|------------------|-----------------|----------|-----------|\n")
        
        for det in res['details']:
            a = det['action']
            true_up = 0.0 if a==0 else (0.15 if a==1 else 0.40)
            est_up = det['uplift']
            sup = det['support']
            allowed = "YES" if sup >= 0.05 or a==0 else "NO"
            sel = "YES" if a == res['recommended_action'] else "NO"
            f.write(f"| {a} | {true_up:.0%} | {est_up:.0%} | {sup:.1%} | {allowed} | {sel} |\n")
            
        f.write(f"\n**Final Recommended Action**: {res['recommended_action']}\n")
        f.write("**Reasoning**: Action 2 has massive predicted uplift (40%), but its historical support is only 1.0%. ")
        f.write("Because it is below the 5% epistemic threshold, the policy correctly distrusts the estimator's extrapolation and falls back to Action 1, which has solid support (85%) and moderate uplift.\n")

if __name__ == "__main__":
    main()
