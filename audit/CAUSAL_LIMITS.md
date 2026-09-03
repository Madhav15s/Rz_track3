# CAUSAL LIMITS AUDIT

## Goal
To identify the specific conditions where causal methods succeed, fail, or require support-aware abstention, rather than blindly assuming causal inference always beats naive baselines.

## Findings by Regime

### 1. The Sweet Spot (Mild Observational Confounding)
- **Where Causal Helps**: Under mild confounding, the T-Learner and DR-Learner successfully strip out the historical bias and accurately map the heterogeneous treatment effects. They recognize that VIPs don't *need* `HUMAN_ESCALATION` to recover, and safely route to cheaper interventions, beating the Naive Propensity baseline.

### 2. The Extrapolation Trap (Strong Observational Confounding)
- **Where Causal Fails**: When historical policies heavily restrict certain actions to specific segments (e.g., `HUMAN_ESCALATION` only for VIPs), basic causal models like T-Learner fail completely. Because they fit separate models per action, they are forced to extrapolate the VIP model onto non-VIP customers. They hallucinate high recovery rates, over-prescribe expensive actions, and perform *worse* than Naive models.
- **Where Naive Wins**: Naive models (single regression without interactions) act as a global smoothing function. They learn that `HUMAN_ESCALATION` is broadly slightly positive, but very expensive. Thus, they safely ignore it and deploy a cheap, broadly effective global static rule (e.g., `RETRY_LATER`), unintentionally avoiding the extrapolation trap.

### 3. The IPW Explosion (Severe Positivity Violation)
- **Where DR-Learner Fails**: Doubly Robust models theoretically correct for confounding via Inverse Probability Weighting (IPW). However, under severe positivity violations, $P(A=a|X)$ approaches zero. The weights explode, destroying the variance of the target variable. Without rigorous cross-fitting and propensity clipping, the DR-Learner collapses, performing worst of all.

### 4. The Blind Spot (Unmeasured Confounding)
- **Where Identification is Impossible**: If treatment was historically assigned based on hidden latents (e.g., urgency, liquidity) that are not passed to the models, Strong Ignorability is violated. The model cannot distinguish the effect of the treatment from the effect of the latent confounder. All models suffer bias. Causal inference *cannot* magically solve unmeasured confounding.

## The Solution: Support-Aware Abstention
The only mathematically robust defense against extrapolation under strong confounding is **Support-Awareness**. 
The `SupportAwareCausalPolicy` explicitly models the historical assignment probability $P(A=a|X)$. If it predicts a counterfactual for an action that a customer has $<10\%$ historical probability of receiving, it **rejects the counterfactual** and abstains.
By recognizing its own epistemic limits, it captures the HTE value where data is dense, and falls back to safe actions where data is sparse, providing the highest robust floor across all regimes.
