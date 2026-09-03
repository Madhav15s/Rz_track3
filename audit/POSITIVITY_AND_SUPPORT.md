# POSITIVITY AND SUPPORT AUDIT

## Goal
To quantify the extent to which observational bias destroys treatment support (positivity) and forces causal models to extrapolate.

## Findings from Propensity Distributions
We analyzed the true assignment probabilities $P(A=a|X)$ across regimes:

1. **RCT Regime (Randomized)**
   - All actions have $P(A=a|X) \approx 16.7\%$.
   - **Support**: Complete. The feature space is perfectly balanced across treatments. Models interpolate safely.

2. **Observational Regime (Observed Confounding)**
   - `HUMAN_ESCALATION` (Action 5) is restricted almost entirely to VIPs.
   - P5 to P95 range: $2.3\%$ to $69.1\%$.
   - **Support**: Severe violation. Low-value customers have virtually zero probability of receiving Human Escalation, yet standard causal models are forced to predict their counterfactual outcome under this treatment.

3. **Unmeasured Regime (Latent Confounding)**
   - Actions are driven by hidden latents.
   - **Support**: Moderate to severe violation. For example, Action 5 (driven by latent value) has a P5 propensity of $4.9\%$. 

## T-Learner Extrapolation Trap
The T-Learner fits a separate sub-model for each action. When fitting the `HUMAN_ESCALATION` sub-model, the training data consists almost exclusively of VIPs (due to the observational policy). The model correctly learns a very high intercept (because VIPs recover easily). 

However, during test-set evaluation, the T-Learner must predict the `HUMAN_ESCALATION` counterfactual for *all* customers. It extrapolates its VIP-trained model onto low-value customers. It hallucinates that low-value customers will also experience massive recovery rates if escalated to humans. The optimizer trusts this hallucination, prescribes the highly expensive `HUMAN_ESCALATION` action, and burns policy value on friction and cost.

## The Need for Support-Awareness
Causal models must not be allowed to blindly output counterfactual predictions in regions where $P(A=a|X) \approx 0$. If a treatment was never historically applied to a specific segment, the model has no empirical basis for its prediction. The policy must recognize this epistemic uncertainty and explicitly abstain.
