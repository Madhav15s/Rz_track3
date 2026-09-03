import subprocess
import json
import numpy as np
import os

def run_seed_audit():
    results = {}
    
    seeds = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    for seed in seeds:
        print(f"Running seed {seed}...")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        
        # 1. Generate data to a tmp dir
        cmd_gen = f"python scripts/generate_data.py --num_customers 500 --seed {seed} --output_dir data/audit_seed_{seed}"
        subprocess.run(cmd_gen, shell=True, check=True, stdout=subprocess.DEVNULL, env=env)
        
        # 2. Run train_and_evaluate by changing data_dir
        cmd_eval = f"python scripts/train_and_evaluate.py --data_dir data/audit_seed_{seed}"
        subprocess.run(cmd_eval, shell=True, check=True, stdout=subprocess.DEVNULL, env=env)
        
        # 3. Read evaluation_results.json
        with open(f"data/audit_seed_{seed}/evaluation_results.json", "r") as f:
            res = json.load(f)
            
        results[seed] = res
        
    # Aggregate
    for model in ["FixedDunning", "T-Learner", "DoublyRobust", "Oracle"]:
        inc = [results[s][model]["incremental_revenue"] for s in seeds]
        net = [results[s][model]["net_incremental_revenue"] for s in seeds]
        print(f"\n--- {model} ---")
        print(f"Incremental Mean: {np.mean(inc):.2f} (Std: {np.std(inc):.2f})")
        print(f"Net Mean: {np.mean(net):.2f} (Std: {np.std(net):.2f})")

if __name__ == "__main__":
    run_seed_audit()
