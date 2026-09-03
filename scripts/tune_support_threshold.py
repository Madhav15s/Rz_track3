import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from backend.app.causal.estimators import SupportAwareCausalPolicy, TLearner
from evaluation.run_fast_benchmark import fast_eval

def main():
    regime = "strong_obs"
    seed = 42
    data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
    
    if not os.path.exists(data_dir):
        print(f"Data for {regime} seed {seed} not found.")
        return
        
    df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
    df_oracle = pd.read_csv(f"{data_dir}/oracle/potential_outcomes.csv")
    
    df_train_full = df_obs[df_obs['split']=='train']
    df_train, df_val = train_test_split(df_train_full, test_size=0.2, random_state=42)
    
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    thresholds = [0.05, 0.10, 0.15, 0.20]
    results = {}
    
    for t in thresholds:
        print(f"Evaluating threshold: {t}")
        policy = SupportAwareCausalPolicy(causal_estimator=TLearner(), min_support=t)
        
        policy.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
        
        models_dict = {f"Support-Aware (t={t})": policy}
        df_val_feat = df_val[['case_id']+features].drop_duplicates('case_id')
        
        res = fast_eval(df_val_feat, df_oracle, models_dict, df_val)
        
        name = f"Support-Aware (t={t})"
        results[t] = {
            'net_incremental_revenue': res[name]['net_incremental_revenue'],
            'intervention_rate': res[name]['intervention_rate'],
            'abstention_rate': res[name]['abstention_rate'],
            'policy_regret': res[name]['policy_regret']
        }
        
    with open("audit/SUPPORT_THRESHOLD_SENSITIVITY.md", "w") as f:
        f.write("# SUPPORT THRESHOLD SENSITIVITY\n\n")
        f.write("Threshold selection performed purely on 20% validation split of the training data (Seed 42, Strong Obs regime).\n\n")
        f.write("| Threshold | Net Incremental Rev | Intervention Rate | Abstention Rate | Policy Regret |\n")
        f.write("|-----------|---------------------|-------------------|-----------------|---------------|\n")
        
        best_t = thresholds[0]
        best_val = -float('inf')
        
        for t in thresholds:
            r = results[t]
            f.write(f"| {t:.0%} | {r['net_incremental_revenue']:,.0f} | {r['intervention_rate']:.2%} | {r['abstention_rate']:.2%} | {r['policy_regret']:,.0f} |\n")
            if r['net_incremental_revenue'] > best_val:
                best_val = r['net_incremental_revenue']
                best_t = t
                
        f.write(f"\n**Selected Threshold:** {best_t:.0%}\n")
        
if __name__ == "__main__":
    main()
