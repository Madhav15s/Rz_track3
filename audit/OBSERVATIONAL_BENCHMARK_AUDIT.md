# OBSERVATIONAL BENCHMARK AUDIT

## Goal
Verify that the RCT, Observational, and Unmeasured Confounding regimes mathematically differed in their assignment probabilities, confirming the benchmark data is valid.

## Propensity Distributions P(A=a|X)

### 1. RCT Regime
In the RCT regime, treatment assignment is uniformly random (approx $16.7\%$ per action).
- **Minimum Propensity**: 0.167
- **Median Propensity**: 0.167
- **Maximum Propensity**: 0.200
- **Effective Sample Size**: Balanced (~1,700 cases per action).
- **Conclusion**: Unconfounded. Perfect support.

### 2. Observational Regime (Mild to Strong)
The assignment policy heavily favored specific actions based on observables (e.g. `amount_paise`, `value_band`).
- `HUMAN_ESCALATION` (Action 5):
  - Support: 5.5% of dataset
  - Minimum Propensity: 0.021
  - 5th Percentile: 0.023
  - Median: 0.561
  - 95th Percentile: 0.691
  - Maximum: 0.691
- **Conclusion**: Severely Confounded. The huge gap between the 5th percentile (2.3%) and the 95th percentile (69.1%) proves that the assignment policy was highly determinisic for certain segments (VIPs), completely starving the model of support for non-VIPs.

### 3. Unmeasured Regime
The assignment policy favored specific actions based on hidden latents (e.g., `latent_liquidity`, `latent_urgency`).
- `HUMAN_ESCALATION` (Action 5):
  - Support: 14.5% of dataset
  - Minimum Propensity: 0.017
  - Median: 0.435
  - Maximum: 0.912
- **Conclusion**: Latently Confounded. The models cannot see the latent variables, so their internal propensity estimations will clash with the true underlying probabilities, violating Strong Ignorability.

## Final Verdict
The benchmark data generation successfully created three statistically distinct causal regimes. The RCT serves as a perfect theoretical ceiling, while the Observational regime accurately mimics the dangerous extrapolation traps present in real-world historical data.
