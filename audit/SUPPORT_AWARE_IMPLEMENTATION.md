# SUPPORT-AWARE CAUSAL POLICY IMPLEMENTATION AUDIT

## Implementation Mechanics
We audited the actual implementation of `SupportAwareCausalPolicy` in `backend/app/causal/estimators.py` and `evaluation/run_fast_benchmark.py`.

**1. How support is calculated**
Support is explicitly modeled as the assignment propensity $P(A=a|X)$. The policy trains a separate `RandomForestClassifier` alongside the main causal estimator. 

**2. Is support action-specific?**
Yes. The propensity model outputs a vector of probabilities corresponding to each available action. When evaluating an action $a$, it checks the specific probability $P(A=a|X)$.

**3. Is support estimated only from training data?**
Yes. The propensity model is fit strictly on the historical training set (`df_features`, `df_treatments`). The test set is only used for forward inference.

**4. What happens when support is insufficient?**
If $P(A=a|X) < \text{min\_support}$ and the action is an intervention ($a \neq 0$), the policy explicitly overrides the predicted uplift to $0.0$. 

**5. What fallback policy is used?**
Because unsupported actions have their uplift set to zero, their expected net incremental value evaluates strictly to their negative costs ($- \text{cost}_a - \text{friction}_a - \text{risk}_a$). As long as costs are positive, these actions will mathematically lose to Action 0 (`DO_NOTHING`), which has 0 uplift and 0 cost. Therefore, the fallback policy is safe abstention (`DO_NOTHING`).

**6. How uncertainty is incorporated**
Currently, epistemic uncertainty (variance of the estimator's prediction due to lack of data) is *not* explicitly modeled using confidence intervals (e.g., via bootstrap or GP variance). Instead, propensity acts as a deterministic proxy for epistemic uncertainty: if we haven't seen the action historically for this profile, we assume infinite uncertainty and veto the action.
