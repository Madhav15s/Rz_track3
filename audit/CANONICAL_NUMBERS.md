# CANONICAL NUMBERS & PRE-FLIGHT CONSISTENCY

## Discrepancy Resolution: 26.8M vs 4.8M Value Saved

**The Discrepancy:**
An earlier diagnostic log temporarily noted ~26,881,146 paise saved, while the final `ABSTENTION_METRIC_FIX.md` explicitly outputs 4,839,818 paise saved.

**The Cause:**
The 26.8M figure was an intermediate placeholder / incomplete calculation generated before the `eval_abstention.py` script was fully corrected to compute `regret_before` vs `regret_after` across the full 5-seed benchmark array. Once the script successfully completed its loop over seeds `[10, 20, 30, 40, 50]` under the `SEVERE_POSITIVITY` regime, the mathematically exact, reproducible aggregate output was 4,839,818 paise.

## Official Benchmark Definitions

This file declares the single source of truth for the Buildathon pitch and documentation.

- **Official Regimes**: `RCT`, `MILD_OBS`, `STRONG_OBS`, `SEVERE_POSITIVITY`, `UNMEASURED`
- **Official Seed Set**: `[10, 20, 30, 40, 50]`
- **Official Dataset Size**: $N = 10,000$ cases per seed.

### Permitted Pitch Numbers

For the Buildathon pitch, you are **officially cleared** to use the following canonical numbers derived from `evaluation/CANONICAL_BENCHMARK.md`:

1. **Abstention Value Saved (Severe Positivity):**
   `4,839,818 paise` (The net economic loss prevented by abstaining from hallucinated causal extrapolations across 5 seeds).

2. **Net Incremental Revenue (Severe Positivity):**
   - **Naive Model:** `90,348,349` paise
   - **T-Learner (Unconstrained):** `78,741,553` paise
   - **Support-Aware Causal Policy:** `79,709,516` paise
   *(Note: The naive model globally acts as a smoothing baseline and won here; the causal claim focuses on Support-Aware successfully stopping the T-Learner from bleeding out completely.)*

3. **Net Incremental Revenue (Strong Observational):**
   - **Naive Model:** `90,348,349` paise
   - **T-Learner (Unconstrained):** `92,684,927` paise
   - **Support-Aware Causal Policy:** `92,184,123` paise
   *(Here, overlap is decent enough that causal identification easily beats naive.)*

**These numbers are strictly reproducible by running `python scripts/run_final_eval.py` and `python scripts/eval_abstention.py`.**
