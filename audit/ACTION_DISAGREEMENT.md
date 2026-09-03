# ACTION DISAGREEMENT AUDIT

## Regime: RCT
- **Naive vs T-Learner**: 45.2% disagreement
- **T-Learner vs DR**: 10.2% disagreement
- **DR vs Support-Aware**: 10.2% disagreement

**Example Disagreement (T-Learner vs Support-Aware)**:
No disagreements found in this sample.

## Regime: STRONG_OBS
- **Naive vs T-Learner**: 41.8% disagreement
- **T-Learner vs DR**: 28.2% disagreement
- **DR vs Support-Aware**: 33.6% disagreement

**Example Disagreement (T-Learner vs Support-Aware)**:
Customer 2: T-Learner chose Action 5, Support-Aware chose Action 2.
Reason: The T-Learner predicted high uplift, but the Support-Aware policy detected it was out-of-support (epistemic uncertainty) and abstained/fell back.

## Regime: SEVERE_POSITIVITY
- **Naive vs T-Learner**: 30.4% disagreement
- **T-Learner vs DR**: 9.6% disagreement
- **DR vs Support-Aware**: 31.0% disagreement

**Example Disagreement (T-Learner vs Support-Aware)**:
Customer 3: T-Learner chose Action 2, Support-Aware chose Action 1.
Reason: The T-Learner predicted high uplift, but the Support-Aware policy detected it was out-of-support (epistemic uncertainty) and abstained/fell back.

