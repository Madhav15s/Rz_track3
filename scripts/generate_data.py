import argparse
import os
import pandas as pd
import numpy as np
from simulator.generators.synthetic_data import SyntheticWorldGenerator
import json
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic causal dataset")
    parser.add_argument("--num_customers", type=int, default=10000, help="Number of customers to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output_dir", type=str, default="data/raw", help="Output directory")
    parser.add_argument("--regime", type=str, choices=["rct", "mild_obs", "strong_obs", "severe_positivity", "unmeasured", "u1", "u2", "u3", "u4"], default="rct", help="Treatment assignment regime")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    gen = SyntheticWorldGenerator(seed=args.seed)
    
    print(f"Generating {args.num_customers} customers...")
    customers = gen.generate_customers(args.num_customers)
    
    print("Generating cases and potential outcomes...")
    cases, outcomes = gen.generate_cases_and_outcomes(customers)
    
    # We need to extract the true probabilities which are currently hidden in the generator output
    # Since generate_cases_and_outcomes doesn't return them, we will quickly re-calculate them here 
    # to avoid modifying the core simulator file and risking breaking other things.
    customer_map = {c.id: c for c in customers}
    
    print(f"Simulating {args.regime} treatment assignment...")
    assignments = []
    observed_outcomes = []
    oracle_records = []
    
    for case, outcome in zip(cases, outcomes):
        cust = customer_map[case.customer_id]
        
        # Re-calculate true probabilities for the oracle file
        logit_p0 = (-2.0 + 3.0 * cust.latent_payment_reliability + 2.0 * cust.latent_liquidity 
                    - 1.0 * (case.failure_code == "INSUFFICIENT_FUNDS") - 1.5 * (case.failure_code == "BANK_DECLINE"))
        p0 = 1 / (1 + np.exp(-logit_p0))
        logit_p1 = logit_p0 + 2.0 * cust.latent_retry_responsiveness - 2.0 * (case.failure_code == "INSUFFICIENT_FUNDS") + 1.5 * (case.failure_code == "BANK_TIMEOUT")
        p1 = 1 / (1 + np.exp(-logit_p1))
        logit_p2 = logit_p0 + 2.5 * cust.latent_delayed_retry_responsiveness + 1.5 * (case.failure_code == "INSUFFICIENT_FUNDS")
        p2 = 1 / (1 + np.exp(-logit_p2))
        logit_p3 = logit_p0 + 2.0 * cust.latent_message_responsiveness
        p3 = 1 / (1 + np.exp(-logit_p3))
        logit_p4 = logit_p0 + 3.0 * cust.latent_alternate_method_responsiveness - 1.0 * (case.payment_method == "netbanking")
        p4 = 1 / (1 + np.exp(-logit_p4))
        logit_p5 = logit_p0 + 4.0 * cust.latent_human_escalation_responsiveness
        p5 = 1 / (1 + np.exp(-logit_p5))
        
        oracle_records.append({
            "case_id": case.id,
            "y_0": outcome.y_0, "y_1": outcome.y_1, "y_2": outcome.y_2, 
            "y_3": outcome.y_3, "y_4": outcome.y_4, "y_5": outcome.y_5,
            "p_0": p0, "p_1": p1, "p_2": p2, "p_3": p3, "p_4": p4, "p_5": p5
        })
        
        # Apply strict eligibility constraints as defined in the governor
        eligible_actions = [0, 1, 2, 3, 4, 5]
        if case.engagement_score < 0.2:
            eligible_actions.remove(5)
            
        # Assignment Logic
        logits = np.zeros(6)
        
        if args.regime == "rct":
            pass # Uniform logits (0.0)
            
        elif args.regime == "mild_obs":
            logits[1] = 0.5 if case.amount_paise < 100000 else 0.0
            logits[2] = 0.5 if case.failure_code == "INSUFFICIENT_FUNDS" else 0.0
            logits[3] = 0.5 if case.engagement_score > 0.7 else 0.0
            logits[4] = 0.0
            logits[5] = 1.0 if case.customer_value_band == "high" else -0.5
            
        elif args.regime == "strong_obs":
            logits[1] = 2.0 if case.amount_paise < 100000 else 0.0
            logits[2] = 2.0 if case.failure_code == "INSUFFICIENT_FUNDS" else 0.0
            logits[3] = 2.0 if case.engagement_score > 0.7 else 0.0
            logits[4] = 1.0
            logits[5] = 3.0 if case.customer_value_band == "high" else -2.0
            
        elif args.regime == "severe_positivity":
            # Intentional severe support violation
            logits[1] = 5.0 if case.amount_paise < 50000 else -5.0
            logits[2] = 5.0 if case.failure_code == "INSUFFICIENT_FUNDS" else -5.0
            logits[3] = 5.0 if case.engagement_score > 0.9 else -5.0
            logits[4] = 0.0
            logits[5] = 10.0 if case.customer_value_band == "high" else -10.0
            
        elif args.regime in ["u1", "u2", "u3", "u4", "unmeasured"]:
            mult = {"u1": 1.0, "u2": 2.0, "u3": 5.0, "u4": 10.0, "unmeasured": 2.0}[args.regime]
            logits[1] = mult * cust.latent_urgency
            logits[2] = mult * cust.latent_liquidity
            logits[3] = mult * cust.latent_digital_engagement
            logits[4] = mult * cust.latent_price_sensitivity
            val_norm = (np.log(cust.latent_customer_value) - 10) / 1.5
            logits[5] = mult * val_norm
            
        # Restrict to eligible actions
        eligible_logits = np.array([logits[a] for a in eligible_actions])
        
        # Softmax
        exp_L = np.exp(eligible_logits)
        probs = exp_L / np.sum(exp_L)
        
        # In severe_positivity, we do NOT mix with 10% uniform. We mix with 0.1% to practically destroy support.
        if args.regime == "severe_positivity":
            probs = 0.999 * probs + 0.001 * (1.0 / len(eligible_actions))
        elif args.regime == "rct":
            probs = 1.0 * probs
        else:
            probs = 0.9 * probs + 0.1 * (1.0 / len(eligible_actions))
        
        assigned_action = gen.rng.choice(eligible_actions, p=probs)
        propensity = probs[eligible_actions.index(assigned_action)]
        
        assignments.append({
            "case_id": case.id,
            "assigned_action": assigned_action,
            "propensity": propensity,
            "eligible_actions": eligible_actions,
            "policy_version": args.regime
        })
        
        y_obs = getattr(outcome, f"y_{assigned_action}")
        observed_outcomes.append({
            "case_id": case.id,
            "assigned_action": assigned_action,
            "y_observed": y_obs
        })

    # Convert to DataFrames
    df_customers = pd.DataFrame([vars(c) for c in customers])
    df_cases = pd.DataFrame([vars(c) for c in cases]).rename(columns={'id': 'case_id'})
    df_oracle = pd.DataFrame(oracle_records)
    df_assignments = pd.DataFrame(assignments)
    df_observed = pd.DataFrame(observed_outcomes)

    # Save full dataset
    df_train_features = df_cases.merge(df_assignments, on="case_id").merge(df_observed, on=["case_id", "assigned_action"])
    
    # SPLIT: 70/15/15 by customer_id
    customer_ids = df_customers['id'].values
    gen.rng.shuffle(customer_ids)
    
    n_train = int(0.7 * len(customer_ids))
    n_val = int(0.15 * len(customer_ids))
    
    train_cust = set(customer_ids[:n_train])
    val_cust = set(customer_ids[n_train:n_train+n_val])
    test_cust = set(customer_ids[n_train+n_val:])
    
    df_train_features['split'] = df_train_features['customer_id'].apply(
        lambda x: 'train' if x in train_cust else ('val' if x in val_cust else 'test')
    )
    
    print("Saving datasets...")
    df_train_features.to_csv(os.path.join(args.output_dir, "observed_data.csv"), index=False)
    
    # Save the ORACLE data completely separately to ensure no leakage
    os.makedirs(os.path.join(args.output_dir, "oracle"), exist_ok=True)
    df_oracle.to_csv(os.path.join(args.output_dir, "oracle", "potential_outcomes.csv"), index=False)
    df_customers.to_csv(os.path.join(args.output_dir, "oracle", "latent_customers.csv"), index=False)

    manifest = {
        "dataset_version": "1.0",
        "num_customers": args.num_customers,
        "seed": args.seed,
        "timestamp": datetime.utcnow().isoformat(),
        "splits": {
            "train": len(train_cust),
            "val": len(val_cust),
            "test": len(test_cust)
        }
    }
    with open(os.path.join(args.output_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print("Data generation complete!")

if __name__ == "__main__":
    main()
