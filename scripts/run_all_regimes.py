import os
import subprocess
import json

def main():
    regimes = ["rct", "mild_obs", "strong_obs", "severe_positivity", "unmeasured"]
    
    # Run the benchmarks
    for regime in regimes:
        print(f"\n======================================")
        print(f"RUNNING REGIME: {regime.upper()}")
        print(f"======================================")
        cmd = f"python evaluation/run_fast_benchmark.py --regime {regime}"
        subprocess.run(cmd, shell=True, check=True)
        
    # Compile the final markdowns
    print("Aggregating results...")
    
    regime_map = {
        "rct": "REGIME A (RCT)",
        "mild_obs": "REGIME B (Mild Obs)",
        "strong_obs": "REGIME C (Strong Obs)",
        "severe_positivity": "REGIME D (Severe Positivity)",
        "unmeasured": "REGIME E (Unmeasured)"
    }
    
    md_support = "# SUPPORT AWARE BENCHMARK ACROSS REGIMES\n\n"
    md_overlap = "# OVERLAP REGIME BENCHMARK\n\n"
    
    for regime, r_name in regime_map.items():
        try:
            with open(f"evaluation/{regime.upper()}_final_benchmark.json", "r") as f:
                data = json.load(f)
                
            summary = data["summary"]
            models = list(summary.keys())
            
            md_support += f"## {r_name}\n"
            md_support += "| Model | Net Incremental Rev | Gross Recovery | Intervention Rate | Abstention Rate | Policy Regret |\n"
            md_support += "|-------|---------------------|----------------|-------------------|-----------------|---------------|\n"
            
            for m in models:
                net = summary[m]['net_incremental_revenue']
                gross = summary[m]['gross_recovery']
                inv = summary[m]['intervention_rate']
                abs_rate = summary[m]['abstention_rate']
                regret = summary[m]['policy_regret']
                md_support += f"| {m} | {net['mean']:,.0f} +/- {net['ci_95'][1]-net['mean']:,.0f} | {gross['mean']:,.0f} | {inv['mean']:.2%} | {abs_rate['mean']:.2%} | {regret['mean']:,.0f} |\n"
            
            md_support += "\n"
        except FileNotFoundError:
            print(f"Missing results for {regime}")
            
    with open("evaluation/SUPPORT_AWARE_BENCHMARK.md", "w") as f:
        f.write(md_support)
        
    with open("evaluation/OVERLAP_REGIME_BENCHMARK.md", "w") as f:
        f.write(md_support) # Same data, different view if needed
        
    print("DONE")

if __name__ == "__main__":
    main()
