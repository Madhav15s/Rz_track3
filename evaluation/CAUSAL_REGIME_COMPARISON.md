# CAUSAL REGIME COMPARISON

This benchmark measures the robustness of causal estimation under three different historical treatment assignment policies (RCT, Observational Confounding, and Unmeasured Confounding). 

*All regimes share the exact same underlying test-set customers and potential outcomes. Only the training set assignment distributions differ.*

## Aggregate Performance (Net Incremental Revenue, N=10,000)

| Model | RCT (Random) | Observational (Confounded) | Unmeasured (Latent Confounding) |
|-------|--------------|----------------------------|---------------------------------|
| Historical Policy | 31.7M | 49.2M | 46.8M |
| Naive Propensity | 90.3M | 90.3M | 90.3M |
| T-Learner | 89.6M | 87.7M | 93.6M |
| DR-Learner | 92.1M | 78.1M | 87.9M |
| **Oracle** | 128.7M | 128.7M | 128.7M |

## Analysis of the Breakdown

**1. The "Naive Propensity" Constant Performance**
The Naive Propensity model fits a single Logistic Regression predicting $P(Y=1|X, A)$. Because it lacks explicit $X \times A$ interactions, it models the effect of every action as a global constant logit shift. Consequently, its optimal policy degenerates into a global static rule (intervening 100% of the time with the mathematically "safest" average action). Because the test-set potential outcomes are identical across regimes, this static policy yields the exact same 90.3M return everywhere. It is completely blind to Heterogeneous Treatment Effects (HTE).

**2. T-Learner Extrapolation Failure (Observational)**
In the Observational regime, treatments are heavily biased (e.g., `HUMAN_ESCALATION` given almost exclusively to VIPs). The T-Learner fits a separate model for each action. The model for `HUMAN_ESCALATION` is trained entirely on high-recovering VIPs, causing it to learn an artificially high intercept. When deployed, it aggressively extrapolates this high recovery probability to non-VIPs, wasting immense friction/risk costs and losing to the Naive baseline (87.7M vs 90.3M). 

**3. DR-Learner Variance Explosion**
The DR-Learner performed best in the RCT regime (92.1M) but collapsed completely in the Observational regime (78.1M). Why? Because observational confounding creates extreme propensity scores (e.g., probability of a low-value customer getting Human Escalation approaches 0). The Inverse Probability Weighting (IPW) step divides by these tiny probabilities, causing massive variance in the pseudo-outcomes. Without cross-fitting, this variance destroys the final effect regressor. 

**4. The Value of RCTs**
The RCT regime provides uniform support across all actions for all customer types. This allows the T-Learner and DR-Learner to accurately map the response surfaces without extrapolation traps, maximizing their HTE routing capabilities. 

## Conclusion
This proves why causal inference is strictly necessary but exceptionally difficult on historical data. A naive predictive model ignores HTE and degenerates into a static rule. A basic causal model (T-Learner) falls into extrapolation traps due to lack of support. Advanced causal debiasing (DR-Learner) explodes in variance without careful cross-fitting and overlap trimming. 
