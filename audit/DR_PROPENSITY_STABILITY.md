# DR PROPENSITY STABILITY AUDIT

In the observational regime, extreme propensities (near 0) cause the Inverse Probability Weighting (IPW) step to explode. This audit compares three strategies for handling IPW instability.

| Estimator | Net Incremental Rev | Policy Regret |
|-----------|---------------------|---------------|
| DR Raw | 92,843,567 | 9,213,178 |
| DR Clipped | 92,164,547 | 6,798,051 |
| DR Stabilized (Overlap) | 90,262,645 | 3,392,555 |
