import pandas as pd
import numpy as np
import os

def main():
    regime = "severe_positivity"
    seeds = [10, 20, 30, 40, 50]
    
    tot_fb_cases = 0
    tot_regret_before = 0
    tot_regret_after = 0
    tot_val_saved = 0
    
    from backend.app.causal.estimators import SupportAwareCausalPolicy, TLearner
    from backend.app.policy.economic_policy import ACTION_CATALOG
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    for seed in seeds:
        data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
        df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
        df_oracle = pd.read_csv(f"{data_dir}/oracle/potential_outcomes.csv")
        df_test = df_obs[df_obs['split']=='test']
        oracle_lookup = df_oracle.set_index('case_id').to_dict(orient='index')
        
        policy = SupportAwareCausalPolicy(causal_estimator=TLearner(), min_support=0.05)
        df_train = df_obs[df_obs['split']=='train']
        policy.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
        
        df_test_feat = df_test[['case_id']+features].drop_duplicates('case_id')
        t_learner = policy.estimator
        
        fallback_cases = 0
        total_regret_before = 0
        total_regret_after = 0
        total_value_saved = 0
        
        for _, row in df_test_feat.iterrows():
            ctx = row.to_dict()
            cid = ctx['case_id']
            amount = ctx['amount_paise']
            true_outs = oracle_lookup[cid]
            y_0 = true_outs['y_0']
            
            true_nets = []
            for a in range(6):
                costs = 0 if a==0 else ACTION_CATALOG[a].cost + ACTION_CATALOG[a].friction + ACTION_CATALOG[a].risk
                true_nets.append(amount * (true_outs[f'y_{a}'] - y_0) - costs)
            
            best_oracle_val = max(true_nets)
            
            res_sa = policy.get_best_action(ctx, None)
            a_sa = res_sa['recommended_action']
            
            best_t_a = 0
            best_t_val = 0.0
            effects = t_learner.predict_all_effects(ctx)
            for a, up in effects.items():
                costs = 0 if a==0 else ACTION_CATALOG[a].cost + ACTION_CATALOG[a].friction + ACTION_CATALOG[a].risk
                c_net = amount * up - costs
                if c_net > best_t_val:
                    best_t_val = c_net
                    best_t_a = a
                    
            if a_sa != best_t_a:
                fallback_cases += 1
                
                true_val_sa = true_nets[a_sa]
                true_val_t = true_nets[best_t_a]
                
                regret_before = best_oracle_val - true_val_t
                regret_after = best_oracle_val - true_val_sa
                
                value_saved = regret_before - regret_after
                
                total_regret_before += regret_before
                total_regret_after += regret_after
                total_value_saved += value_saved
                
        tot_fb_cases += fallback_cases
        tot_regret_before += total_regret_before
        tot_regret_after += total_regret_after
        tot_val_saved += total_value_saved
            
    with open("audit/ABSTENTION_METRIC_FIX.md", "w") as f:
        f.write("# ABSTENTION METRIC FIX\n\n")
        f.write("Evaluating cases where the Support-Aware policy vetoed the underlying T-Learner's decision due to insufficient historical support.\n\n")
        f.write(f"**Regime**: {regime.upper()} | **Seeds**: {seeds}\n\n")
        f.write("### Metric Definitions\n")
        f.write("- **regret_before**: `oracle_value - true_value(t_learner_action)`\n")
        f.write("- **regret_after**: `oracle_value - true_value(support_aware_action)`\n")
        f.write("- **value_saved**: `regret_before - regret_after`. A positive number means the support-aware fallback actively prevented economic loss compared to trusting the blind causal estimate.\n\n")
        f.write(f"- **Total Fallback Cases**: {tot_fb_cases}\n")
        f.write(f"- **Total Regret Before (T-Learner)**: {tot_regret_before:,.0f} paise\n")
        f.write(f"- **Total Regret After (Support-Aware)**: {tot_regret_after:,.0f} paise\n")
        f.write(f"- **Total Value Saved**: {tot_val_saved:,.0f} paise\n")

if __name__ == "__main__":
    main()
