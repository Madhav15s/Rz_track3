# FINAL CAUSAL FINDINGS

## Core Scientific Question
*"Under what conditions does our causal recovery policy actually create measurable policy-value improvement over a strong naïve recovery baseline?"*

Based on the multi-regime structural audit (RCT, Mild, Strong, Severe Positivity, and Unmeasured Confounding), a causal recovery policy outperforms a naive predictive baseline **if and only if all four of the following conditions are met:**

### 1. The Presence of Heterogeneous Treatment Effects (HTE)
There must be actual variation in how different customer segments respond to treatments (e.g., `RETRY_LATER` works uniquely well for `INSUFFICIENT_FUNDS`). If interventions shift everyone's recovery probability equally, a naive global model is sufficient.

### 2. Mild to Moderate Observational Confounding
The historical data must feature biased treatment assignments (e.g., VIPs historically receiving `HUMAN_ESCALATION`), which forces naive models to wrongly attribute the VIPs' natural recovery to the human action. However, the confounding cannot be so absolute that strict deterministic rules were followed. There must be enough "exploration" or noise in the historical logs (Positivity) for the causal models to map the counterfactual response surface.

### 3. Support-Aware Abstention (Epistemic Safety)
Under severe confounding, basic causal models (like the standard T-Learner) perform *worse* than naive models. When faced with a customer completely outside the historical support for an action (e.g., a low-value customer considering `HUMAN_ESCALATION`), the T-Learner extrapolates wildly and hallucinates massive uplift. 
**The causal policy only wins when paired with Support-Aware Abstention**, which explicitly blocks interventions if $P(A=a|X) < \text{threshold}$, deferring to safe baseline actions instead of trusting out-of-support counterfactuals.

### 4. Unconfoundedness (Strong Ignorability)
The variables that drove historical treatment assignment must be visible to the model ($X$). If the historical agents assigned treatments based on hidden latent variables (like `latent_liquidity`), the causal estimators are mathematically indistinguishable from naive models in their bias. Causal ML algorithms do not magically solve unmeasured confounding; they only untangle *measured* confounding.

## Conclusion for the Buildathon Pitch
The naive strategy is equivalent to saying: "Find the action that is correlated with the highest recovery rate." Because VIPs recover the most, it just recommends whatever we gave to VIPs. 

Our causal strategy is equivalent to saying: "Find the action that caused the highest *change* in recovery rate, but **only if** we have enough historical evidence for this specific customer profile to prove it."

By deploying a **Support-Aware Causal Policy**, we avoid the naive trap of correlation, whilst mathematically immunizing ourselves against the causal trap of out-of-support extrapolation. This structural safety is the true breakthrough of the architecture.
