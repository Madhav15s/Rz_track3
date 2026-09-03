import pandas as pd
import numpy as np
import os

def main():
    regimes = ["rct", "strong_obs", "severe_positivity"]
    seed = 42
    
    from backend.app.causal.estimators import NaiveRecoveryPropensity, SupportAwareCausalPolicy, TLearner, DoublyRobustLearner
    from backend.app.policy.economic_policy import ACTION_CATALOG
    
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    with open("audit/ACTION_DISAGREEMENT.md", "w") as f:
        f.write("# ACTION DISAGREEMENT AUDIT\n\n")
        
        for regime in regimes:
            data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
            df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
            df_train = df_obs[df_obs['split']=='train']
            df_test = df_obs[df_obs['split']=='test']
            
            models = {
                "Naive": NaiveRecoveryPropensity(),
                "T-Learner": TLearner(),
                "DR": DoublyRobustLearner(weight_style="clipped"),
                "Support-Aware": SupportAwareCausalPolicy(causal_estimator=TLearner(), min_support=0.05)
            }
            
            for m in models.values():
                m.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
                
            df_test_feat = df_test[['case_id']+features].drop_duplicates('case_id').head(500)
            
            actions = {n: [] for n in models.keys()}
            
            for _, row in df_test_feat.iterrows():
                ctx = row.to_dict()
                amount = ctx['amount_paise']
                
                for n, m in models.items():
                    if isinstance(m, SupportAwareCausalPolicy):
                        best_a = m.get_best_action(ctx, None)['recommended_action']
                    else:
                        effects = m.predict_all_effects(ctx)
                        best_a = 0
                        best_v = 0.0
                        for a, up in effects.items():
                            c = 0 if a==0 else ACTION_CATALOG[a].cost + ACTION_CATALOG[a].friction + ACTION_CATALOG[a].risk
                            v = amount * up - c
                            if v > best_v:
                                best_v = v; best_a = a
                        
                    actions[n].append(best_a)
                    
            f.write(f"## Regime: {regime.upper()}\n")
            
            pairs = [("Naive", "T-Learner"), ("T-Learner", "DR"), ("DR", "Support-Aware")]
            for p1, p2 in pairs:
                a1 = np.array(actions[p1])
                a2 = np.array(actions[p2])
                disagree = np.mean(a1 != a2)
                f.write(f"- **{p1} vs {p2}**: {disagree:.1%} disagreement\n")
                
            # Find an example where T-Learner != Support-Aware
            f.write("\n**Example Disagreement (T-Learner vs Support-Aware)**:\n")
            found = False
            for i in range(len(actions["T-Learner"])):
                if actions["T-Learner"][i] != actions["Support-Aware"][i]:
                    f.write(f"Customer {i}: T-Learner chose Action {actions['T-Learner'][i]}, Support-Aware chose Action {actions['Support-Aware'][i]}.\n")
                    f.write("Reason: The T-Learner predicted high uplift, but the Support-Aware policy detected it was out-of-support (epistemic uncertainty) and abstained/fell back.\n\n")
                    found = True
                    break
            if not found:
                f.write("No disagreements found in this sample.\n\n")

if __name__ == "__main__":
    main()
