import pandas as pd
import numpy as np
import os
import json
from collections import defaultdict
from backend.app.causal.estimators import NaiveRecoveryPropensity, SupportAwareCausalPolicy, TLearner, DoublyRobustLearner
from scripts.run_final_eval import run_regime

def main():
    regimes = ["u1", "u2", "u3", "u4"]
    seed = 42 # Run a single representative seed for the stress test
    
    final_output = "# IDENTIFICATION STRESS TEST (UNMEASURED CONFOUNDING)\n\n"
    final_output += "Increasing treatment-assignment dependence on hidden variables.\n\n"
    final_output += "| Regime | Model | Net Incremental Rev | Policy Regret | Oracle Capture |\n"
    final_output += "|--------|-------|---------------------|---------------|----------------|\n"
    
    for regime in regimes:
        print(f"Running {regime}...")
        res, _ = run_regime(regime, seed)
        
        models = ["Naive Recovery Model", "T-Learner", "DR-Learner", "Support-Aware Causal Policy", "Oracle"]
        
        for m in models:
            net = res[m]['net']
            regret = res[m]['regret']
            cap = net / res['Oracle']['net'] if res['Oracle']['net'] > 0 else 0
            
            final_output += f"| {regime.upper()} | {m} | {net:,.0f} | {regret:,.0f} | {cap:.2%} |\n"
            
    with open("audit/UNMEASURED_STRESS_TEST.md", "w") as f:
        f.write(final_output)

if __name__ == "__main__":
    main()
