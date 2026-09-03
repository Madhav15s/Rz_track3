# PROPENSITY VS CAUSAL: FINAL AUDIT

## Why the earlier mathematical claim is invalid
An earlier audit claimed that "optimizing a propensity model and a causal model will mathematically result in 0% disagreement because $P(Y=1|X,A) - P(Y=1|X,A=0)$ preserves the exact same ranking." 

While algebraically true for raw probability rankings, it is **fundamentally false in our economic implementation.**

Our `economic_policy` optimizer selects actions by computing Net Incremental Value:
`net_value = amount * predicted_uplift - costs`

### The Propensity Trap
The `PropensityLearner` and `NaiveRecoveryPropensity` models output the **gross probability of recovery** ($P(Y=1|X,A)$) rather than the true incremental uplift. 
When this gross probability is passed to the optimizer as if it were the uplift, the optimizer computes:
`net_value = amount * P(Y=1|X,A) - costs`

This massively overestimates the incremental value of the action. For example, if a customer has an 85% chance of paying naturally, and an intervention raises it to 90%, the true value is `amount * 5%`. However, the propensity model tricks the optimizer into thinking the intervention caused the *entire 90%*, resulting in `amount * 90%`. 

Because of this inflation, the optimizer justifies highly expensive, high-friction actions (like `HUMAN_ESCALATION`) that would otherwise be rejected.

### The Disagreement
This is why the `ACTION_DISAGREEMENT` audit found:
- RCT: 45.2% disagreement
- STRONG_OBS: 41.8% disagreement
- SEVERE_POSITIVITY: 30.4% disagreement

The naive predictive models wildly over-intervene with expensive actions, whereas the T-Learner (Causal) subtracts the natural baseline $P(Y=1|X,A=0)$ and correctly rejects expensive actions if the marginal gain is too small. 

Therefore, any previous claims that causal and propensity policies are "mathematically identical" are officially deprecated and removed. The causal T-Learner behaves radically differently by isolating the marginal effect.
