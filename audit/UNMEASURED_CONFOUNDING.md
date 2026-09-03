# UNMEASURED CONFOUNDING REGIME

## Goal
To introduce a stress test where the historical treatment assignment is confounded by variables that the machine learning models cannot see. This represents a fundamental limitation of causal inference from observational data.

## Latent Assignment Policy
In this regime, the historical policy assigns treatments based on hidden latents:
1. `RETRY_NOW`: biased by `latent_urgency`.
2. `RETRY_LATER`: biased by `latent_liquidity`.
3. `PAYMENT_MESSAGE`: biased by `latent_digital_engagement` (which is noisily proxied by observables, but the exact latent is hidden).
4. `ALTERNATE_METHOD`: biased by `latent_price_sensitivity`.
5. `HUMAN_ESCALATION`: biased by `latent_customer_value`.

## Impact on Causal Inference
A core assumption of observational causal inference is **Strong Ignorability (Unconfoundedness)**: $Y(a) \perp A \mid X$. This assumes that all variables influencing both treatment and outcome are measured and included in $X$.

By explicitly driving treatment assignment with unmeasured latents (like `latent_urgency`), we violate Strong Ignorability. 

## Expected Behavior
Because the models cannot see the unmeasured confounders:
1. **Bias**: Even the T-Learner and DR-Learner will exhibit bias in their treatment effect estimates, as they cannot mathematically distinguish the effect of the treatment from the effect of the hidden latent variable.
2. **Confidence / Abstention**: Under severe unmeasured confounding or poor overlap, predicted confidence intervals should widen. The desired system behavior is to gracefully degrade by abstaining (choosing `NO_ACTION`) when the variance/uncertainty of the estimated uplift exceeds the expected value margin, avoiding costly interventions based on unreliable evidence.
3. **Limitation Documentation**: We explicitly document that a causal estimator does *not* magically solve unmeasured confounding. Real-world mitigation requires either randomized exploration (A/B testing) or instrumental variables, rather than purely algorithmic debiasing.
