import pandas as pd
import numpy as np
import json
import os
import subprocess
import warnings
import sys

# Suppress sklearn/pandas warnings for cleaner output
warnings.filterwarnings('ignore')

from backend.app.causal.estimators import TLearner, DoublyRobustLearner, PropensityLearner
from backend.app.causal.baselines import DoNothingBaseline, FixedDunningBaseline
from backend.app.policy.economic_policy import EconomicPolicyOptimizer, DeterministicPolicyGovernor, ACTION_CATALOG
from scripts.train_and_evaluate import evaluate_policy_on_oracle

def eval_policy_augmented(df_features, df_oracle, policy_fn):
    """Augmented evaluation tracking gross recovery & policy regret."""
    total_incremental_revenue = 0.0
    total_net_incremental_revenue = 0.0
    total_gross_recovery = 0.0
    total_oracle_net_value = 0.0
    
    action_counts = {a: 0 for a in range(6)}
    oracle_dict = df_oracle.set_index('case_id').to_dict(orient='index')
    
    for _, row in df_features.iterrows():
        ctx = row.to_dict()
        action = policy_fn(ctx)
        action_counts[action] += 1
        
        case_id = ctx['case_id']
        true_outcomes = oracle_dict[case_id]
        y_0 = true_outcomes['y_0']
        y_a = true_outcomes[f'y_{action}']
        
        amount = ctx['amount_paise']
        
        # Gross
        total_gross_recovery += (y_a * amount)
        
        # Incremental
        true_uplift = y_a - y_0
        incremental_rev = true_uplift * amount
        total_incremental_revenue += incremental_rev
        
        # Costs & Net
        cfg = ACTION_CATALOG[action]
        costs = cfg.cost + cfg.friction + cfg.risk
        net_rev = incremental_rev - costs
        total_net_incremental_revenue += net_rev
        
        # Oracle best possible for this case
        best_val = 0.0
        for cand_a in range(6):
            c_uplift = true_outcomes[f'y_{cand_a}'] - y_0
            c_cfg = ACTION_CATALOG[cand_a]
            c_net = (amount * c_uplift) - c_cfg.cost - c_cfg.friction - c_cfg.risk
            if c_net > best_val:
                best_val = c_net
        
        total_oracle_net_value += best_val
        
    interventions = sum(v for k, v in action_counts.items() if k != 0)
    total_cases = len(df_features)
    
    return {
        "incremental_revenue": float(total_incremental_revenue),
        "net_incremental_revenue": float(total_net_incremental_revenue),
        "gross_recovery": float(total_gross_recovery),
        "policy_regret": float(total_oracle_net_value - total_net_incremental_revenue),
        "interventions": interventions,
        "intervention_rate": float(interventions / total_cases),
        "abstention_rate": float(action_counts[0] / total_cases)
    }

def run_seed(seed: int, num_customers: int = 500):
    print(f"\n--- Running Seed {seed} ---")
    
    # 1. Generate data
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    data_dir = f"data/benchmark_seed_{seed}"
    cmd_gen = f"python scripts/generate_data.py --num_customers {num_customers} --seed {seed} --output_dir {data_dir}"
    subprocess.run(cmd_gen, shell=True, check=True, stdout=subprocess.DEVNULL, env=env)
    
    df_obs = pd.read_csv(os.path.join(data_dir, "observed_data.csv"))
    df_oracle = pd.read_csv(os.path.join(data_dir, "oracle", "potential_outcomes.csv"))
    
    df_train = df_obs[df_obs['split'] == 'train']
    df_test = df_obs[df_obs['split'] == 'test']
    
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    df_features_train = df_train[['case_id'] + features]
    df_treatments_train = df_train[['case_id', 'assigned_action', 'propensity']]
    df_outcomes_train = df_train[['case_id', 'assigned_action', 'y_observed']]
    
    models = {
        "Do Nothing": DoNothingBaseline(),
        "Fixed Dunning": FixedDunningBaseline(),
        "Propensity": PropensityLearner(),
        "T-Learner": TLearner(),
        "DR-Learner": DoublyRobustLearner()
    }
    
    results = {}
    governor = DeterministicPolicyGovernor()
    
    df_features_test = df_test[['case_id'] + features].drop_duplicates('case_id')
    oracle_lookup = df_oracle.set_index('case_id').to_dict(orient='index')
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(df_features_train, df_treatments_train, df_outcomes_train)
        optimizer = EconomicPolicyOptimizer(model)
        
        def policy_fn(ctx):
            decision = optimizer.get_best_action(ctx)
            action = decision['recommended_action']
            gov_check = governor.evaluate(ctx, action)
            if gov_check['status'] == 'REJECTED':
                return 0
            return action
            
        metrics = eval_policy_augmented(df_features_test, df_oracle, policy_fn)
        results[name] = metrics
        
    # Oracle Policy
    def oracle_policy_fn(ctx):
        best_a = 0
        best_val = 0.0
        amount = ctx['amount_paise']
        true_outcomes = oracle_lookup[ctx['case_id']]
        for a in range(6):
            true_uplift = true_outcomes[f'y_{a}'] - true_outcomes['y_0']
            cfg = ACTION_CATALOG[a]
            net_val = (amount * true_uplift) - cfg.cost - cfg.friction - cfg.risk
            if net_val > best_val:
                gov_check = governor.evaluate(ctx, a)
                if gov_check['status'] == 'APPROVED':
                    best_val = net_val
                    best_a = a
        return best_a

    results["Oracle"] = eval_policy_augmented(df_features_test, df_oracle, oracle_policy_fn)
    return results

def main():
    seeds = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    all_results = {}
    
    # Check reproducibility first
    print("Checking Reproducibility (Seed 42 x 2)...")
    res_42_1 = run_seed(42)
    res_42_2 = run_seed(42)
    
    # Compare
    for m in res_42_1.keys():
        if res_42_1[m]['net_incremental_revenue'] != res_42_2[m]['net_incremental_revenue']:
            print("REPRODUCIBILITY FAILURE!")
            sys.exit(1)
    print("Reproducibility: PASSED.")
    
    for s in seeds:
        all_results[s] = run_seed(s)
        
    models = list(all_results[10].keys())
    metrics = ["incremental_revenue", "net_incremental_revenue", "gross_recovery", "intervention_rate", "abstention_rate", "policy_regret"]
    
    summary = {}
    for m in models:
        summary[m] = {}
        for metric in metrics:
            vals = [all_results[s][m][metric] for s in seeds]
            mean = float(np.mean(vals))
            std = float(np.std(vals))
            # 95% CI roughly 1.96 * std / sqrt(N)
            ci = 1.96 * std / np.sqrt(len(seeds))
            summary[m][metric] = {
                "mean": mean,
                "std": std,
                "ci_95": [mean - ci, mean + ci]
            }
            
    with open("evaluation/final_benchmark.json", "w") as f:
        json.dump({"raw": all_results, "summary": summary}, f, indent=2)
        
    # Generate MD
    md = "# Final Causal Benchmark\n\n"
    md += "## Aggregate Results (10 Seeds)\n"
    md += "| Model | Net Incremental Rev | Gross Recovery | Intervention Rate | Policy Regret |\n"
    md += "|-------|---------------------|----------------|-------------------|---------------|\n"
    for m in models:
        net = summary[m]['net_incremental_revenue']
        gross = summary[m]['gross_recovery']
        inv = summary[m]['intervention_rate']
        regret = summary[m]['policy_regret']
        md += f"| {m} | {net['mean']:,.0f} ± {net['ci_95'][1]-net['mean']:,.0f} | {gross['mean']:,.0f} | {inv['mean']:.2%} | {regret['mean']:,.0f} |\n"
        
    with open("evaluation/FINAL_CAUSAL_BENCHMARK.md", "w") as f:
        f.write(md)

if __name__ == "__main__":
    main()
