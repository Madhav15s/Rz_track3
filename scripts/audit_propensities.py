import pandas as pd
import numpy as np
import os
import json

def main():
    regimes = ["rct", "observational", "unmeasured"]
    seed = 42
    
    for regime in regimes:
        data_dir = f"data/benchmark_{regime}_n10k_seed_{seed}"
        if not os.path.exists(data_dir):
            continue
            
        df_obs = pd.read_csv(f"{data_dir}/observed_data.csv")
        
        print(f"\n======================================")
        print(f"REGIME: {regime.upper()}")
        print(f"======================================")
        
        for a in range(6):
            df_a = df_obs[df_obs['assigned_action'] == a]
            if len(df_a) == 0:
                print(f"Action {a}: 0 samples")
                continue
                
            props = df_a['propensity'].values
            
            p_min = np.min(props)
            p5 = np.percentile(props, 5)
            p_med = np.median(props)
            p95 = np.percentile(props, 95)
            p_max = np.max(props)
            
            p_A = len(df_a) / len(df_obs)
            
            print(f"Action {a} | Support: {len(df_a)} ({p_A:.1%})")
            print(f"  P(A=a|X) stats: min={p_min:.3f}, p5={p5:.3f}, med={p_med:.3f}, p95={p95:.3f}, max={p_max:.3f}")
            
if __name__ == "__main__":
    main()
