# MODEL POLICY DISAGREEMENT AUDIT

## Investigation Goal
To trace the policy path and prove whether the standard Propensity Learner (predicting gross recovery $P(Y=1|a)$) and the T-Learner (predicting causal uplift $P(Y=1|a) - P(Y=1|0)$) make differing decisions, and to explain why the N=500 benchmark yielded exactly identical Net Incremental Revenue.

## Mathematical Trace
The pipeline separates causal prediction from economic optimization. 
The `EconomicPolicyOptimizer` selects the action that maximizes `inc_value`:

$$ \text{inc\_value}_a = (\text{amount} \times \text{effect}_a) - \text{costs}_a $$

### Case 1: T-Learner
The T-Learner outputs true uplift:
- $\text{effect}_a = P_a - P_0$
- $\text{effect}_0 = 0$

Thus, the optimizer compares:
- Value of Action $a$: $V_a^{T} = \text{amount} \times (P_a - P_0) - \text{costs}_a$
- Value of Action $0$: $V_0^{T} = 0$

The T-Learner prefers action $a$ over $0$ iff:
$$ \text{amount} \times P_a - \text{amount} \times P_0 - \text{costs}_a > 0 $$
$$ \text{amount} \times P_a - \text{costs}_a > \text{amount} \times P_0 $$

### Case 2: Propensity Learner
The Propensity Learner outputs gross probability:
- $\text{effect}_a = P_a$
- $\text{effect}_0 = P_0$

Thus, the optimizer compares:
- Value of Action $a$: $V_a^{P} = \text{amount} \times P_a - \text{costs}_a$
- Value of Action $0$: $V_0^{P} = \text{amount} \times P_0$

The Propensity Learner prefers action $a$ over $0$ iff:
$$ \text{amount} \times P_a - \text{costs}_a > \text{amount} \times P_0 $$

## Conclusion: 0% Disagreement Rate
The inequalities for the `argmax` are algebraically identical. Because our utility function is strictly linear with respect to the probability of recovery, **predicting the causal uplift and maximizing net incremental value is mathematically isomorphic to predicting gross conversion and maximizing absolute net value.**

**Disagreement Rate: 0.0%**

The T-Learner and the Propensity Learner are making the exact same internal decisions on every single case. The $14.1\%$ reported gain of T-Learner over Fixed Dunning is real, but it is NOT because it has magical "causal" powers over a standard ML propensity model. A standard Propensity model achieves the exact same optimal routing because subtracting $P_0$ is mathematically equivalent to keeping $P_0$ and comparing the absolute values. 

The only exception occurs if the DR-Learner is used, where the inverse probability weighting actually alters the learned coefficients compared to the raw empirical probabilities, or if the utility function becomes non-linear. But between T-Learner and Propensity, they are functionally identical policies.
