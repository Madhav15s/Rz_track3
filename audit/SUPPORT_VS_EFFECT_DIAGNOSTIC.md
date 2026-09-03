# SUPPORT VS CAUSAL EFFECT DIAGNOSTIC

Demonstrating how the policy behaves when confronted with a high-effect but low-support action.

| Action | True Uplift (Simulated) | Estimated Uplift | Support P(A\|X) | Allowed? | Selected? |
|--------|-------------------------|------------------|-----------------|----------|-----------|
| 0 | 0% | 0% | 10.0% | YES | NO |
| 1 | 15% | 15% | 85.0% | YES | YES |
| 2 | 40% | 0% | 1.0% | NO | NO |

**Final Recommended Action**: 1
**Reasoning**: Action 2 has massive predicted uplift (40%), but its historical support is only 1.0%. Because it is below the 5% epistemic threshold, the policy correctly distrusts the estimator's extrapolation and falls back to Action 1, which has solid support (85%) and moderate uplift.
