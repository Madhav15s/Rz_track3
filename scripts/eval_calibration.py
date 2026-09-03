import pandas as pd
import numpy as np

def main():
    regime = "strong_obs"
    seed = 42
    data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
    
    df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
    df_oracle = pd.read_csv(f"{data_dir}/oracle/potential_outcomes.csv")
    df_test = df_obs[df_obs['split']=='test']
    
    from backend.app.causal.estimators import TLearner
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    model = TLearner()
    df_train = df_obs[df_obs['split']=='train']
    model.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
    
    df_test_feat = df_test[['case_id']+features].drop_duplicates('case_id')
    oracle_lookup = df_oracle.set_index('case_id').to_dict(orient='index')
    
    buckets = {
        "0-5%": [],
        "5-10%": [],
        "10-20%": [],
        "20-40%": [],
        "40%+": []
    }
    
    p0 = model._predict_proba_a(df_test_feat, 0) if hasattr(model, '_predict_proba_a') else np.zeros(len(df_test_feat))
    
    for a in range(1, 6):
        pa = model._predict_proba_a(df_test_feat, a)
        pred_uplifts = pa - p0
        
        true_y_a = df_oracle[f'y_{a}'].values
        true_y_0 = df_oracle['y_0'].values
        true_uplifts = true_y_a - true_y_0
        
        for i in range(len(pred_uplifts)):
            pred_up = pred_uplifts[i]
            true_up = true_uplifts[i]
            
            if pred_up < 0.05: b = "0-5%"
            elif pred_up < 0.10: b = "5-10%"
            elif pred_up < 0.20: b = "10-20%"
            elif pred_up < 0.40: b = "20-40%"
            else: b = "40%+"
            
            buckets[b].append((pred_up, true_up))
            
    with open("audit/COUNTERFACTUAL_CALIBRATION.md", "w") as f:
        f.write("# COUNTERFACTUAL CALIBRATION AUDIT\n\n")
        f.write("| Predicted Bucket | Avg Predicted Uplift | Avg True Uplift | Count |\n")
        f.write("|------------------|----------------------|-----------------|-------|\n")
        
        for b in ["0-5%", "5-10%", "10-20%", "20-40%", "40%+"]:
            if not buckets[b]: continue
            preds = [x[0] for x in buckets[b]]
            trues = [x[1] for x in buckets[b]]
            f.write(f"| {b} | {np.mean(preds):.2%} | {np.mean(trues):.2%} | {len(preds)} |\n")
            
if __name__ == "__main__":
    main()
