# FINAL CAUSAL VALUE VALIDATION

## 1. Does causal modeling actually add value under observational treatment assignment?
Yes, but only if handled with extreme care regarding overlap and support. Under severe observational confounding, basic causal models (like T-Learner) can actually *lose* to naive predictive models because they extrapolate wildly into regions where they have no historical training data (e.g., predicting how a low-value customer will respond to a VIP-only treatment). Causal modeling adds value by attempting to isolate true uplift, but it demands algorithmic safety constraints to prevent costly out-of-support predictions.

## 2. Does T-Learner beat the naive propensity model?
It depends entirely on the regime. 
In the **Unmeasured Confounding** regime, the T-Learner successfully leveraged its HTE routing to beat the Naive model (93.6M vs 90.3M). 
However, in the strictly **Observational** regime, the T-Learner fell into a severe extrapolation trap due to lack of overlap, trailing the Naive model (87.7M vs 90.3M). The Naive model degenerated into a safe, global static rule, whereas the T-Learner burned money trying to apply VIP treatments to non-VIPs based on confounded historical intercepts.

## 3. Does DR beat T-Learner under observed confounding?
**No. It performed significantly worse.**
Under severe observed confounding, the propensity scores $\pi(A=a|X)$ approach 0 for certain customer/action pairs. The DR-Learner divides the target variable by these propensity scores (Inverse Probability Weighting). This division by near-zero causes the variance of the pseudo-outcomes to explode. Because our DR-Learner lacks cross-fitting and strict propensity trimming, this variance destroyed the final model, resulting in a severe performance collapse (78.1M vs T-Learner's 87.7M).

## 4. What happens under unmeasured confounding?
When the true drivers of treatment assignment are hidden from the model (e.g., `latent_urgency`, `latent_liquidity`), the fundamental assumption of causal inference (Strong Ignorability) is violated. The models incorrectly attribute the uplift caused by the latent variable to the action itself. While the T-Learner still managed to eke out a win based on the observable proxies, its confidence metrics are fundamentally untrustworthy.

## 5. Does the system appropriately abstain when evidence is insufficient?
No, and this is the critical missing piece. The current pipeline forces a prediction and optimizes expected value even when the causal estimator is extrapolating wildly out-of-support (as seen in the Observational regime). To safely deploy causal estimators, the system must calculate epistemic uncertainty (or check propensity overlap) and actively **abstain** from high-cost interventions when the customer falls outside the historical support of that action.

## 6. How much oracle policy value does each method capture?
Across the regimes, the Oracle consistently achieves ~128.7M Net Incremental Revenue.
- **Naive Propensity**: Captured ~69.6% (by reverting to a safe global rule).
- **T-Learner**: Captured between 68% (Observational) and 72.3% (Unmeasured).
- **DR-Learner**: Captured 70.7% (RCT) but dropped to 60.6% (Observational) due to variance explosion.

## 7. Which benchmark should be the primary buildathon claim?
**The Observational Benchmark.**
It mathematically proves the core dilemma of the product: historical payment data is biased. Naive ML models ignore this bias and degenerate into static rules. Standard causal models (T-Learner) hallucinate out-of-support. The winning buildathon claim must be that our architecture will fuse causal debiasing with strict Governor-level epistemic uncertainty checks to safely route payments without falling into extrapolation traps. The RCT benchmark is merely a theoretical ceiling, not a realistic historical dataset.
