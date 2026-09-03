# NAIVE MODEL REGIME AUDIT

## Investigation Goal
Investigate why the `Naive Recovery Propensity` model achieved the exact same Net Incremental Revenue (90,348,349 paise) across all three distinct treatment assignment regimes (RCT, Observational, Unmeasured).

## Finding: The Constant Global Action
The Naive Propensity model is implemented as a single Logistic Regression predicting $P(Y=1 | X, A)$. Crucially, it treats the assigned action $A$ as just another categorical feature without full interaction terms ($X \times A$). 

Because there are no interactions, the learned effect of an action $A=a$ is modeled as a constant logit shift added to the customer's baseline recovery probability. 
In all three regimes, the model learned that Action 2 (`RETRY_LATER`) had the most favorable ratio of global positive coefficient to financial cost (Action 2 is cheap and broadly effective).

When predicting optimal actions on the test set, the Naive model selected **Action 2 for 100% of the test cases**, regardless of the regime.

## Why the Scores Matched Perfectly
1. The Naive model degenerated into a static policy (always choose Action 2).
2. The synthetic dataset generation ensures that the underlying potential outcomes ($Y(a)$) for a given random seed are generated purely from the customer features and latents. 
3. Only the *assigned* treatments in the training set varied between regimes. The test-set ground truth remained identical.
4. Because the Naive model applied the exact same static rule to the exact same test-set cases, the resulting policy value was mathematically identical across all regimes.

## Conclusion
The identical result is not a code bug in the evaluation pipeline. It correctly demonstrates the fundamental flaw of naive predictive models in heterogeneous treatment settings: they average the treatment effect across the entire population and fail to learn conditional routing. In this scenario, applying Action 2 everywhere happened to yield 90.3M, setting a powerful but un-intelligent baseline.
