# FINAL CAUSAL THESIS

Based on the multi-regime empirical evidence and the identification stress testing, our final architectural thesis for the Razorpay AI Buildathon is:

**"Support-aware causal decisioning: estimate incremental intervention effects where historical evidence supports the counterfactual, and abstain when it does not."**

## Scientific Justification

- **Under mild/moderate confounding with adequate overlap**, causal estimation successfully isolates and identifies useful heterogeneous treatment effects, accurately routing customers to optimal interventions and creating measurable net policy value above naive baselines.
- **Under poor overlap (Severe Positivity, Strong Observational bias)**, unconstrained causal models extrapolate blindly into data-sparse regions. As proven by our counterfactual calibration audit, when the base T-Learner predicted an extreme uplift bucket of **40%+**, the true simulated uplift was only **~18.82%**. This catastrophic miscalibration in the tails proves that unconstrained models hallucinate effects for treatments that were historically impossible for those segments. Left unguarded, they perform worse than simple naive models because they recommend wildly expensive actions (e.g. `HUMAN_ESCALATION`) based on this hallucinated uplift.
- **Therefore**, explicit support/overlap awareness and epistemic abstention are strictly required before automating a counterfactual intervention. The true product value of our `CausalRecover` architecture is this structural safety net: we only deploy causal decisions when the historical propensity mathematically justifies it.
- **Under unmeasured confounding**, causal identification remains fundamentally limited. Our models do not magically unconfound hidden latents. They survive these regimes only because the support-aware wrapper safely abstains from extreme estimations, and because the latents partially leak through observable proxies.

Standard Machine Learning captures correlations but ignores Heterogeneous Treatment Effects. Standard Causal ML captures Heterogeneous Treatment Effects but hallucinates wildly under historical bias. Only a **Support-Aware Causal Policy** limits the optimizer to regions of epistemic certainty, providing mathematically safe uplift.
