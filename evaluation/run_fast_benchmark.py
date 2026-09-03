import pandas as pd
import numpy as np
import json
import os
import subprocess
import warnings
from concurrent.futures import ProcessPoolExecutor

warnings.filterwarnings('ignore')

from backend.app.causal.estimators import TLearner, DoublyRobustLearner, PropensityLearner
from backend.app.causal.baselines import DoNothingBaseline, FixedDunningBaseline
from backend.app.policy.economic_policy import EconomicPolicyOptimizer, DeterministicPolicyGovernor, ACTION_CATALOG

def fast_eval(df_features, df_oracle, models_dict, df_test=None):
    """Batched evaluation"""
    results = {name: {'inc': 0, 'net': 0, 'gross': 0, 'interventions': 0, 'abstentions': 0, 'oracle_val': 0} for name in models_dict}
    results['Oracle'] = {'inc': 0, 'net': 0, 'gross': 0, 'interventions': 0, 'abstentions': 0, 'oracle_val': 0}
    
    oracle_lookup = df_oracle.set_index('case_id').to_dict(orient='index')
    governor = DeterministicPolicyGovernor()
    
    # Pre-predict all effects for all rows at once to save overhead!
    pre_preds = {}
    for name, model in models_dict.items():
        if name in ["Do Nothing", "Historical Policy", "Fixed Dunning"]:
            continue
        # Batch predict
        pre_preds[name] = {}
        from backend.app.causal.estimators import PropensityLearner, NaiveRecoveryPropensity, SupportAwareCausalPolicy
        
        base_model = model.estimator if isinstance(model, SupportAwareCausalPolicy) else model
        
        if isinstance(base_model, PropensityLearner) or isinstance(base_model, NaiveRecoveryPropensity):
            for a in range(6):
                ctx_df = df_features.copy()
                if isinstance(base_model, NaiveRecoveryPropensity):
                    ctx_df['assigned_action'] = a
                pre_preds[name][a] = base_model._predict_proba_a(ctx_df, a) if hasattr(base_model, '_predict_proba_a') else base_model.model.predict_proba(ctx_df)[:, 1]
        elif isinstance(base_model, TLearner):
            p0 = base_model._predict_proba_a(df_features, 0) if hasattr(base_model, '_predict_proba_a') else np.zeros(len(df_features))
            for a in range(6):
                if a == 0: pre_preds[name][a] = np.zeros(len(df_features))
                else: pre_preds[name][a] = base_model._predict_proba_a(df_features, a) - p0
        elif isinstance(base_model, DoublyRobustLearner):
            for a in range(6):
                if a == 0 or a not in base_model.effect_models: pre_preds[name][a] = np.zeros(len(df_features))
                else: pre_preds[name][a] = base_model.effect_models[a].predict(df_features)
                
        # Support scores
        if isinstance(model, SupportAwareCausalPolicy):
            pre_preds[name]['_support'] = model.propensity_model.predict_proba(df_features)

    # Now evaluate row by row
    idx = 0
    
    if df_test is not None:
        historical_actions = df_test.set_index('case_id')['assigned_action'].to_dict()
    else:
        historical_actions = {}
        
    for _, row in df_features.iterrows():
        ctx = row.to_dict()
        cid = ctx['case_id']
        amount = ctx['amount_paise']
        true_outcomes = oracle_lookup[cid]
        y_0 = true_outcomes['y_0']
        
        # Oracle best
        best_val = 0.0
        best_oracle_a = 0
        for cand_a in range(6):
            c_net = amount * (true_outcomes[f'y_{cand_a}'] - y_0) - ACTION_CATALOG[cand_a].cost - ACTION_CATALOG[cand_a].friction - ACTION_CATALOG[cand_a].risk
            if c_net > best_val:
                best_val = c_net
                best_oracle_a = cand_a
        
        # Record Oracle
        results['Oracle']['oracle_val'] += best_val
        results['Oracle']['net'] += best_val
        results['Oracle']['inc'] += amount * (true_outcomes[f'y_{best_oracle_a}'] - y_0)
        results['Oracle']['gross'] += amount * true_outcomes[f'y_{best_oracle_a}']
        if best_oracle_a != 0: results['Oracle']['interventions'] += 1
        else: results['Oracle']['abstentions'] += 1
        
        # Models
        for name, model in models_dict.items():
            if name == "Do Nothing": a = 0
            elif name == "Fixed Dunning": a = 1 if ctx.get('retries_attempted', 0) == 0 else 2
            elif name == "Historical Policy": a = historical_actions.get(cid, 0)
            else:
                # Find best action from pre_preds
                best_a = 0
                best_val = 0.0
                for cand_a in range(6):
                    uplift = pre_preds[name][cand_a][idx]
                    
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
            
            gov = governor.evaluate(ctx, a)
            if gov['status'] == 'REJECTED': a = 0
            
            y_a = true_outcomes[f'y_{a}']
            results[name]['gross'] += amount * y_a
            results[name]['inc'] += amount * (y_a - y_0)
            results[name]['net'] += amount * (y_a - y_0) - ACTION_CATALOG[a].cost - ACTION_CATALOG[a].friction - ACTION_CATALOG[a].risk
            results[name]['oracle_val'] += best_val
            if a != 0: results[name]['interventions'] += 1
            else: results[name]['abstentions'] += 1
            
        idx += 1
        
    final_res = {}
    total = len(df_features)
    for name, r in results.items():
        final_res[name] = {
            "incremental_revenue": r['inc'],
            "net_incremental_revenue": r['net'],
            "gross_recovery": r['gross'],
            "policy_regret": r['oracle_val'] - r['net'],
            "intervention_rate": r['interventions'] / total,
            "abstention_rate": r['abstentions'] / total
        }
    return final_res

def run_seed_fast(seed: int, regime: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
    cmd_gen = f"python scripts/generate_data.py --num_customers 10000 --seed {seed} --regime {regime} --output_dir {data_dir}"
    subprocess.run(cmd_gen, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    
    df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
    df_oracle = pd.read_csv(f"{data_dir}/oracle/potential_outcomes.csv")
    df_train, df_test = df_obs[df_obs['split']=='train'], df_obs[df_obs['split']=='test']
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    from backend.app.causal.estimators import NaiveRecoveryPropensity, SupportAwareCausalPolicy
    
    models = {
        "Do Nothing": DoNothingBaseline(),
        "Historical Policy": DoNothingBaseline(), # Placeholder, will implement actual historical evaluation
        "Naive Propensity": NaiveRecoveryPropensity(),
        "Propensity": PropensityLearner(),
        "T-Learner": TLearner(),
        "DR-Learner": DoublyRobustLearner(weight_style="clipped"),
        "Support-Aware Causal": SupportAwareCausalPolicy(causal_estimator=TLearner(), min_support=0.05)
    }
    
    for name, model in models.items():
        if name == "Historical Policy": continue
        model.fit(df_train[['case_id']+features], df_train[['case_id','assigned_action','propensity']], df_train[['case_id','assigned_action','y_observed']])
        
    return seed, fast_eval(df_test[['case_id']+features].drop_duplicates('case_id'), df_oracle, models, df_test)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", type=str, default="rct")
    args = parser.parse_args()
    
    seeds = [42, 42] + list(range(10, 60, 10))
    all_res = {}
    
    print(f"Running N=10,000 evaluations for regime {args.regime}. This may take a few minutes...")
    for i, seed in enumerate(seeds):
        print(f"Running seed {seed}...")
        if i == 1: 
            s, res = run_seed_fast(seed, args.regime)
            all_res["42_dup"] = res
        else:
            s, res = run_seed_fast(seed, args.regime)
            all_res[seed] = res
                
    for m in all_res[42].keys():
        if all_res[42][m]['net_incremental_revenue'] != all_res["42_dup"][m]['net_incremental_revenue']:
            print("REPRODUCIBILITY FAILURE!")
            os._exit(1)
            
    del all_res["42_dup"]
    del all_res[42]
    
    models = list(all_res[10].keys())
    metrics = ["incremental_revenue", "net_incremental_revenue", "gross_recovery", "intervention_rate", "abstention_rate", "policy_regret"]
    summary = {}
    for m in models:
        summary[m] = {}
        for metric in metrics:
            vals = [all_res[s][m][metric] for s in range(10, 60, 10)]
            mean = float(np.mean(vals))
            std = float(np.std(vals))
            ci = 1.96 * std / np.sqrt(5)
            summary[m][metric] = {"mean": mean, "std": std, "ci_95": [mean-ci, mean+ci]}
            
    for m in models:
        capture_rates = []
        for s in range(10, 60, 10):
            oracle_val = all_res[s]['Oracle']['net_incremental_revenue']
            model_val = all_res[s][m]['net_incremental_revenue']
            capture_rates.append(model_val / oracle_val if oracle_val > 0 else 0)
        mean_cap = float(np.mean(capture_rates))
        std_cap = float(np.std(capture_rates))
        ci_cap = 1.96 * std_cap / np.sqrt(5)
        summary[m]['oracle_capture_rate'] = {"mean": mean_cap, "std": std_cap, "ci_95": [mean_cap-ci_cap, mean_cap+ci_cap]}

    with open(f"evaluation/{args.regime.upper()}_final_benchmark.json", "w") as f:
        json.dump({"raw": all_res, "summary": summary}, f, indent=2)
        
    md = f"# Causal Benchmark ({args.regime.upper()} Regime)\n\n## Aggregate Results (5 Seeds)\n"
    md += "| Model | Net Incremental Rev | Gross Recovery | Intervention Rate | Abstention Rate | Policy Regret | Oracle Capture |\n"
    md += "|-------|---------------------|----------------|-------------------|-----------------|---------------|----------------|\n"
    for m in models:
        net = summary[m]['net_incremental_revenue']
        gross = summary[m]['gross_recovery']
        inv = summary[m]['intervention_rate']
        abs_rate = summary[m]['abstention_rate']
        regret = summary[m]['policy_regret']
        cap = summary[m]['oracle_capture_rate']
        md += f"| {m} | {net['mean']:,.0f} +/- {net['ci_95'][1]-net['mean']:,.0f} | {gross['mean']:,.0f} | {inv['mean']:.2%} | {abs_rate['mean']:.2%} | {regret['mean']:,.0f} | {cap['mean']:.2%} |\n"
        
    with open(f"evaluation/{args.regime.upper()}_BENCHMARK.md", "w") as f:
        f.write(md)
    print("DONE")
