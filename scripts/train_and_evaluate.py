import pandas as pd
import numpy as np
import argparse
import os
import json

from backend.app.causal.estimators import TLearner, DoublyRobustLearner
from backend.app.causal.baselines import DoNothingBaseline, FixedDunningBaseline
from backend.app.policy.economic_policy import EconomicPolicyOptimizer, DeterministicPolicyGovernor, ACTION_CATALOG

def evaluate_policy_on_oracle(df_features, df_oracle, policy_fn):
    """
    Evaluates a given policy function (mapping feature dict -> action) 
    against the true potential outcomes from the oracle.
    """
    total_incremental_revenue = 0.0
    total_net_incremental_revenue = 0.0
    action_counts = {a: 0 for a in range(6)}
    
    # Pre-index oracle for O(1) lookup to avoid merging
    oracle_dict = df_oracle.set_index('case_id').to_dict(orient='index')
    
    for _, row in df_features.iterrows():
        # ONLY OBSERVABLES are passed to the policy. 
        # y_0...y_5 do not exist in df_features.
        ctx = row.to_dict()
        action = policy_fn(ctx)
        action_counts[action] += 1
        
        # Oracle true outcomes lookup AFTER action is selected
        case_id = ctx['case_id']
        true_outcomes = oracle_dict[case_id]
        y_0 = true_outcomes['y_0']
        y_a = true_outcomes[f'y_{action}']
        
        amount = ctx['amount_paise']
        
        # True Causal Uplift
        true_uplift = y_a - y_0
        incremental_rev = true_uplift * amount
        total_incremental_revenue += incremental_rev
        
        cfg = ACTION_CATALOG[action]
        costs = cfg.cost + cfg.friction + cfg.risk
        net_rev = incremental_rev - costs
        
        total_net_incremental_revenue += net_rev
        
    return {
        "incremental_revenue": total_incremental_revenue,
        "net_incremental_revenue": total_net_incremental_revenue,
        "interventions": sum(v for k, v in action_counts.items() if k != 0),
        "action_distribution": action_counts
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/raw")
    args = parser.parse_args()
    
    print("Loading data...")
    df_obs = pd.read_csv(os.path.join(args.data_dir, "observed_data.csv"))
    df_oracle = pd.read_csv(os.path.join(args.data_dir, "oracle", "potential_outcomes.csv"))
    
    df_train = df_obs[df_obs['split'] == 'train']
    df_test = df_obs[df_obs['split'] == 'test']
    
    features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score', 'payment_method', 'failure_code', 'customer_value_band']
    
    # We pass the full dataframe to fit, which merges internally on case_id
    # But wait, our fit signatures expect df_features, df_treatments, df_outcomes
    # df_obs has all of them. Let's split them back for the API.
    
    df_features_train = df_train[['case_id'] + features]
    df_treatments_train = df_train[['case_id', 'assigned_action', 'propensity']]
    df_outcomes_train = df_train[['case_id', 'assigned_action', 'y_observed']]
    
    models = {
        "DoNothing": DoNothingBaseline(),
        "FixedDunning": FixedDunningBaseline(),
        "T-Learner": TLearner(),
        "DoublyRobust": DoublyRobustLearner()
    }
    
    results = {}
    governor = DeterministicPolicyGovernor()
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(df_features_train, df_treatments_train, df_outcomes_train)
        
        optimizer = EconomicPolicyOptimizer(model)
        
        def policy_fn(ctx):
            decision = optimizer.get_best_action(ctx)
            action = decision['recommended_action']
            gov_check = governor.evaluate(ctx, action)
            if gov_check['status'] == 'REJECTED':
                return 0 # Abstain/No Action
            return action
            
        print(f"Evaluating {name} on test set...")
        df_features_test = df_test[['case_id'] + features].drop_duplicates('case_id')
        metrics = evaluate_policy_on_oracle(df_features_test, df_oracle, policy_fn)
        results[name] = metrics
        print(metrics)
        
    # Oracle Policy (Upper Bound)
    print("Evaluating Oracle Policy...")
    
    # We pre-index the oracle to use it in the oracle policy
    oracle_lookup = df_oracle.set_index('case_id').to_dict(orient='index')
    
    def oracle_policy_fn(ctx):
        best_a = 0
        best_val = 0.0
        amount = ctx['amount_paise']
        case_id = ctx['case_id']
        
        true_outcomes = oracle_lookup[case_id]
        
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

    # DO NOT merge with df_oracle here since evaluate_policy_on_oracle already does it
    df_features_test_oracle = df_test[['case_id'] + features].drop_duplicates('case_id')
    metrics = evaluate_policy_on_oracle(df_features_test_oracle, df_oracle, oracle_policy_fn)
    results["Oracle"] = metrics
    print(metrics)
    
    # Format pandas sum values to float
    for k, v in results.items():
        v['incremental_revenue'] = float(v['incremental_revenue'])
        v['net_incremental_revenue'] = float(v['net_incremental_revenue'])
        
    with open(os.path.join(args.data_dir, "evaluation_results.json"), "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
