import pandas as pd
import numpy as np
import os
import json
from backend.app.causal.estimators import NaiveRecoveryPropensity

def main():
    regimes = ["rct", "observational", "unmeasured"]
    seed = 42
    
    results = {}
    test_cases_actions = {}
    
    for regime in regimes:
        data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
        if not os.path.exists(data_dir):
            print(f"Skipping {regime}, data not found.")
            continue
            
        df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
        df_train, df_test = df_obs[df_obs['split']=='train'], df_obs[df_obs['split']=='test']
        features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
        
        model = NaiveRecoveryPropensity()
        model.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
        
        # Get coefficients
        clf = model.model.named_steps['classifier']
        feature_names = model.model.named_steps['preprocessor'].get_feature_names_out()
        
        coef_dict = dict(zip(feature_names, clf.coef_[0]))
        results[regime] = coef_dict
        
        # Predict actions for the first 1000 test cases
        test_cases = df_test[['case_id']+features].drop_duplicates('case_id').head(1000)
        actions_chosen = []
        
        for _, row in test_cases.iterrows():
            ctx = row.to_dict()
            best_a = 0
            best_val = 0.0
            p0 = model.predict_effect(ctx, 0)
            amount = ctx['amount_paise']
            
            # Simulate optimizer
            for a in range(6):
                pa = model.predict_effect(ctx, a)
                cost = 0 if a == 0 else [100, 100, 50, 200, 2500][a-1]
                friction = 0 if a == 0 else [50, 20, 100, 150, 50][a-1]
                risk = 0 if a == 0 else [20, 10, 10, 30, 10][a-1]
                total_cost = cost + friction + risk
                
                val = amount * pa - total_cost
                if val > best_val:
                    best_val = val
                    best_a = a
            actions_chosen.append(best_a)
            
        test_cases_actions[regime] = actions_chosen
        
    for regime in regimes:
        if regime in results:
            print(f"--- {regime.upper()} ---")
            action_coefs = {k: v for k, v in results[regime].items() if 'assigned_action' in k}
            print("Action Coefficients:", action_coefs)
            
            actions = test_cases_actions[regime]
            unique, counts = np.unique(actions, return_counts=True)
            print("Action distribution (first 1000):", dict(zip(unique, counts)))
            
if __name__ == "__main__":
    main()
