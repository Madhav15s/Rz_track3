import pandas as pd
import json
import os
import ast

def audit_leakage():
    issues = []
    
    # Check data files
    df_obs = pd.read_csv("data/raw/observed_data.csv")
    oracle_cols = [f"y_{i}" for i in range(6)]
    
    for col in oracle_cols:
        if col in df_obs.columns:
            issues.append(f"LEAKAGE: {col} found in observed_data.csv")
            
    # Check evaluation script for structural leakage
    with open("scripts/train_and_evaluate.py", "r") as f:
        content = f.read()
        
    if "df = df_features.merge(df_oracle, on='case_id')" in content and "ctx = row.to_dict()" in content:
        issues.append("STRUCTURAL LEAKAGE: evaluate_policy_on_oracle merges df_features and df_oracle, then calls policy_fn(row.to_dict()). This exposes y_0..y_5 to the inference function.")
        
    return issues

if __name__ == "__main__":
    issues = audit_leakage()
    if issues:
        print("LEAKAGE DETECTED:")
        for issue in issues:
            print("-", issue)
        with open("audit/leakage_audit_result.txt", "w") as f:
            f.write("\n".join(issues))
        exit(1)
    else:
        print("No immediate data-file leakage detected.")
        exit(0)
