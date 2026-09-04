# Support Attack Results

**Objective:** Verify that the system's causal policy governor strictly refuses to execute recommended actions when the causal support is extremely low, regardless of the predicted uplift.

## Test Cases Executed

### Scenario A: Extremely High Uplift, Low Support
- **Parameters:** Estimated Uplift = +40%, Support = 1%
- **Result:** The Causal Policy engine strictly limits confidence to `LOW` and evaluates minimum support thresholds. The action is marked as `ABSTAINED` due to violating the `min_support` threshold (0.05).
- **Execution:** When the frontend or agent attempts to execute this, the candidate action is either not selected or rejected. 

### Scenario B: Moderate Uplift, High Support
- **Parameters:** Estimated Uplift = +20%, Support = 60%
- **Result:** Confidence evaluates to `HIGH`. The action passes the support filter and proceeds to the Economic Policy Governor. 
- **Execution:** Successfully evaluated for incremental economic value, and authorized if the value is > 0.

## Conclusion
The Support-Aware Causal framework mathematically forbids extrapolation into unsafe regions. The minimum support threshold is strictly evaluated in `SupportAwareCausalPolicy`, guaranteeing that high-variance or unsupported counterfactuals never trigger real financial mutations.
