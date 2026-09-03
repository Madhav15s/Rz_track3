import pandas as pd
import numpy as np
import os
import json
from backend.app.causal.estimators import DoublyRobustLearner
from evaluation.run_fast_benchmark import fast_eval

def main():
    seed = 42
    regime = "observational"
    data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
    if not os.path.exists(data_dir):
        print("Observational data not found for seed 42.")
        return
        
    df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
    df_oracle = pd.read_csv(f"{data_dir}/oracle/potential_outcomes.csv")
    df_train, df_test = df_obs[df_obs['split']=='train'], df_obs[df_obs['split']=='test']
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    models = {
        "DR Raw": DoublyRobustLearner(weight_style="raw"),
        "DR Clipped": DoublyRobustLearner(weight_style="clipped"),
        "DR Stabilized (Overlap)": DoublyRobustLearner(weight_style="overlap")
    }
    
    print("Fitting DR models...")
    for name, model in models.items():
        print(f"Fitting {name}...")
        model.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
        
    print("Evaluating DR models...")
    df_test_feat = df_test[['case_id']+features].drop_duplicates('case_id')
    res = fast_eval(df_test_feat, df_oracle, models, df_test)
    
    print("\n--- DR STABILITY RESULTS (OBSERVATIONAL REGIME, SEED 42) ---")
    for name in models.keys():
        net = res[name]['net_incremental_revenue']
        regret = res[name]['policy_regret']
        print(f"{name}: Net Incremental = {net:,.0f} | Policy Regret = {regret:,.0f}")
        
    with open("audit/DR_PROPENSITY_STABILITY.md", "w") as f:
        f.write("# DR PROPENSITY STABILITY AUDIT\n\n")
        f.write("In the observational regime, extreme propensities (near 0) cause the Inverse Probability Weighting (IPW) step to explode. "
                "This audit compares three strategies for handling IPW instability.\n\n")
        f.write("| Estimator | Net Incremental Rev | Policy Regret |\n")
        f.write("|-----------|---------------------|---------------|\n")
        for name in models.keys():
            net = res[name]['net_incremental_revenue']
            regret = res[name]['policy_regret']
            f.write(f"| {name} | {net:,.0f} | {regret:,.0f} |\n")
        
if __name__ == "__main__":
    main()
