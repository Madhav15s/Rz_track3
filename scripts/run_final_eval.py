import pandas as pd
import numpy as np
import os
import json
from collections import defaultdict
from backend.app.causal.estimators import NaiveRecoveryPropensity, SupportAwareCausalPolicy, TLearner, DoublyRobustLearner, PropensityLearner
from backend.app.causal.baselines import DoNothingBaseline, FixedDunningBaseline
from backend.app.policy.economic_policy import ACTION_CATALOG

def run_regime(regime, seed=42):
    data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
    if not os.path.exists(data_dir):
        os.system(f"python scripts/generate_data.py --regime {regime} --num_customers 10000 --seed {seed} --output_dir {data_dir}")
        
    df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
    df_oracle = pd.read_csv(f"{data_dir}/oracle/potential_outcomes.csv")
    
    df_train = df_obs[df_obs['split']=='train']
    df_test = df_obs[df_obs['split']=='test']
    
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    models = {
        "Do Nothing": DoNothingBaseline(),
        "Historical Policy": DoNothingBaseline(),
        "Fixed Dunning": FixedDunningBaseline(),
        "Naive Recovery Model": NaiveRecoveryPropensity(),
        "T-Learner": TLearner(),
        "DR-Learner": DoublyRobustLearner(weight_style="clipped"),
        "Support-Aware Causal Policy": SupportAwareCausalPolicy(causal_estimator=TLearner(), min_support=0.05)
    }
    
    for name, model in models.items():
        if name in ["Do Nothing", "Historical Policy", "Fixed Dunning"]: continue
        model.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
        
    df_test_feat = df_test[['case_id']+features].drop_duplicates('case_id')
    oracle_lookup = df_oracle.set_index('case_id').to_dict(orient='index')
    historical_actions = df_test.set_index('case_id')['assigned_action'].to_dict()
    
    pre_preds = {}
    for name, model in models.items():
        if name in ["Do Nothing", "Historical Policy", "Fixed Dunning"]: continue
        pre_preds[name] = {}
        base_model = model.estimator if isinstance(model, SupportAwareCausalPolicy) else model
        
        if isinstance(base_model, NaiveRecoveryPropensity):
            for a in range(6):
                ctx_df = df_test_feat.copy()
                ctx_df['assigned_action'] = a
                pre_preds[name][a] = base_model.model.predict_proba(ctx_df)[:, 1]
        elif isinstance(base_model, TLearner):
            p0 = base_model._predict_proba_a(df_test_feat, 0) if hasattr(base_model, '_predict_proba_a') else np.zeros(len(df_test_feat))
            for a in range(6):
                if a == 0: pre_preds[name][a] = np.zeros(len(df_test_feat))
                else: pre_preds[name][a] = base_model._predict_proba_a(df_test_feat, a) - p0
        elif isinstance(base_model, DoublyRobustLearner):
            for a in range(6):
                if a == 0 or a not in base_model.effect_models: pre_preds[name][a] = np.zeros(len(df_test_feat))
                else: pre_preds[name][a] = base_model.effect_models[a].predict(df_test_feat)
                
        if isinstance(model, SupportAwareCausalPolicy):
            pre_preds[name]['_support'] = model.propensity_model.predict_proba(df_test_feat)
            
    results = {name: {'gross': 0, 'natural': 0, 'inc': 0, 'net': 0, 'interventions': 0, 'abstentions': 0, 'regret': 0, 'actions': [], 'preds': {}} for name in models.keys()}
    results['Oracle'] = {'gross': 0, 'natural': 0, 'inc': 0, 'net': 0, 'interventions': 0, 'abstentions': 0, 'regret': 0, 'actions': []}
    
    abstention_regret_avoided = 0
    calibration_data = []
    
    idx = 0
    for _, row in df_test_feat.iterrows():
        ctx = row.to_dict()
        cid = ctx['case_id']
        amount = ctx['amount_paise']
        true_outs = oracle_lookup[cid]
        y_0 = true_outs['y_0']
        
        best_oracle_val = 0.0
        best_oracle_a = 0
        for cand_a in range(6):
            c_net = amount * (true_outs[f'y_{cand_a}'] - y_0) - (0 if cand_a==0 else ACTION_CATALOG[cand_a].cost + ACTION_CATALOG[cand_a].friction + ACTION_CATALOG[cand_a].risk)
            if c_net > best_oracle_val:
                best_oracle_val = c_net
                best_oracle_a = cand_a
                
        results['Oracle']['net'] += best_oracle_val
        results['Oracle']['inc'] += amount * (true_outs[f'y_{best_oracle_a}'] - y_0)
        results['Oracle']['natural'] += amount * y_0
        results['Oracle']['gross'] += amount * true_outs[f'y_{best_oracle_a}']
        if best_oracle_a != 0: results['Oracle']['interventions'] += 1
        else: results['Oracle']['abstentions'] += 1
        results['Oracle']['actions'].append(best_oracle_a)
        
        for name, model in models.items():
            if name == "Do Nothing": a = 0
            elif name == "Fixed Dunning": a = 1 if ctx.get('retries_attempted', 0) == 0 else 2
            elif name == "Historical Policy": a = historical_actions.get(cid, 0)
            else:
                best_a = 0
                best_val = 0.0
                for cand_a in range(6):
                    uplift = pre_preds[name][cand_a][idx]
                    
                    if name == "T-Learner" and cand_a != 0:
                        true_up = true_outs[f'y_{cand_a}'] - y_0
                        calibration_data.append((uplift, true_up))
                        
                    if isinstance(model, SupportAwareCausalPolicy):
                        support = pre_preds[name]['_support'][idx, cand_a] if cand_a < pre_preds[name]['_support'].shape[1] else 0.0
                        if cand_a != 0 and support < model.min_support:
                            continue
                            
                    cfg = ACTION_CATALOG.get(cand_a)
                    if not cfg: continue
                    c_net = (amount * uplift) - cfg.cost - cfg.friction - cfg.risk
                    if c_net > best_val:
                        best_val = c_net
                        best_a = cand_a
                a = best_a
                
            # Compute actual outcome of chosen action a
            actual_inc = amount * (true_outs[f'y_{a}'] - y_0)
            cfg = ACTION_CATALOG.get(a)
            actual_costs = 0 if a==0 else cfg.cost + cfg.friction + cfg.risk
            actual_net = actual_inc - actual_costs
            
            results[name]['net'] += actual_net
            results[name]['inc'] += actual_inc
            results[name]['natural'] += amount * y_0
            results[name]['gross'] += amount * true_outs[f'y_{a}']
            results[name]['regret'] += (best_oracle_val - actual_net)
            results[name]['actions'].append(a)
            
            if a != 0: results[name]['interventions'] += 1
            else: results[name]['abstentions'] += 1
            
            if name == "Support-Aware Causal Policy" and a == 0:
                # Calculate regret avoided by abstaining compared to T-Learner
                # Wait, this is tricky. We'll approximate by comparing T-Learner's action net vs 0.
                pass 
                
        idx += 1
        
    return results, calibration_data

if __name__ == "__main__":
    regimes = ["rct", "mild_obs", "strong_obs", "severe_positivity", "unmeasured"]
    seeds = [10, 20, 30, 40, 50]
    
    final_output = "# FINAL FIVE-REGIME BENCHMARK\n\n"
    
    for regime in regimes:
        print(f"Running {regime}...")
        agg = defaultdict(lambda: defaultdict(list))
        all_calib = []
        
        for seed in seeds:
            print(f"  Seed {seed}...")
            res, calib = run_regime(regime, seed)
            all_calib.extend(calib)
            for m in res:
                agg[m]['gross'].append(res[m]['gross'])
                agg[m]['natural'].append(res[m]['natural'])
                agg[m]['inc'].append(res[m]['inc'])
                agg[m]['net'].append(res[m]['net'])
                agg[m]['interventions'].append(res[m]['interventions'] / (res[m]['interventions'] + res[m]['abstentions']) if (res[m]['interventions'] + res[m]['abstentions']) > 0 else 0)
                agg[m]['abstentions'].append(res[m]['abstentions'] / (res[m]['interventions'] + res[m]['abstentions']) if (res[m]['interventions'] + res[m]['abstentions']) > 0 else 0)
                agg[m]['regret'].append(res[m]['regret'])
                agg[m]['oracle_capture'].append(res[m]['net'] / res['Oracle']['net'] if res['Oracle']['net'] > 0 else 0)
                
        final_output += f"## REGIME: {regime.upper()}\n"
        final_output += "| Model | Gross Recovery | Natural Recovery | Incremental Recovery | Net Incremental | Intervention Rate | Abstention Rate | Policy Regret | Oracle Capture |\n"
        final_output += "|-------|----------------|------------------|----------------------|-----------------|-------------------|-----------------|---------------|----------------|\n"
        
        for m in agg:
            metrics_str = []
            for col in ['gross', 'natural', 'inc', 'net', 'interventions', 'abstentions', 'regret', 'oracle_capture']:
                arr = agg[m][col]
                mean_val = np.mean(arr)
                std_val = np.std(arr)
                ci_val = 1.96 * std_val / np.sqrt(len(arr))
                
                if col in ['interventions', 'abstentions', 'oracle_capture']:
                    metrics_str.append(f"{mean_val:.2%} ± {std_val:.2%} (CI: ±{ci_val:.2%})")
                else:
                    metrics_str.append(f"{mean_val:,.0f} ± {std_val:,.0f} (CI: ±{ci_val:,.0f})")
                    
            final_output += f"| {m} | {' | '.join(metrics_str)} |\n"
        final_output += "\n"
        
    with open("evaluation/CANONICAL_BENCHMARK.md", "w") as f:
        f.write(final_output)
        
    print("DONE")
