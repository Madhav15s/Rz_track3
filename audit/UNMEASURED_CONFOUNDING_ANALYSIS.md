# UNMEASURED CONFOUNDING ANALYSIS

## Variables and Accessibility
In the "Unmeasured" regime, the simulator directly uses five latent variables to generate the treatment assignment logits:
1. `latent_urgency` -> `RETRY_NOW`
2. `latent_liquidity` -> `RETRY_LATER`
3. `latent_digital_engagement` -> `PAYMENT_MESSAGE`
4. `latent_price_sensitivity` -> `ALTERNATE_METHOD`
5. `latent_customer_value` -> `HUMAN_ESCALATION`

**Crucially, these latent variables are structurally withheld from the policy's feature set ($X$).** The causal estimators only see their noisy proxies (e.g., `engagement_score`, `amount_paise`, `failure_code`). 

## Does Causal Inference "Solve" Unmeasured Confounding?
**No.** It is a mathematical impossibility for standard causal inference to solve unmeasured confounding. Because the unmeasured latents drive both the true potential outcomes and the treatment assignment, the models suffer from fundamental omitted variable bias. The estimated uplift functions $\hat{\tau}(X)$ are mathematically biased.

## Why did Support-Aware still perform well?
Despite the bias in effect estimation, the `Support-Aware Causal Policy` maintained high Net Incremental Revenue in the Unmeasured regime. This is **not** because it magically unconfounded the data, but due to three structural factors:

1. **Observable Proxies**: The simulator generates the observable features directly from the latents (e.g., `engagement_score` is a noisy function of `latent_digital_engagement`). The models implicitly learned partial unconfounding through these proxies.
2. **Abstention mitigates worst-case errors**: Even when the causal model hallucinates an uplift due to unmeasured confounding, the `Support-Aware` wrapper checks the propensity model $P(A=a|X_{obs})$. If the proxy features indicate this action was historically rare for this profile, it abstains, preventing the model from acting on the most extreme (and thus most dangerous) biased estimates.
3. **Confounding directionality**: In our simulator, treatments were naturally assigned to the segments that benefited most (e.g., `latent_liquidity` drives `RETRY_LATER`). Because the historical policy was somewhat rational, the unmeasured bias was positive confounding. The causal models simply "over-trusted" the historical policy where support existed, which happened to still be financially viable.

## Conclusion
We do not claim our method solves unmeasured confounding. We claim that **abstention based on observable support safely limits the damage** caused by unmeasured confounding by explicitly rejecting extrapolations in data-sparse regions.
