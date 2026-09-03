# Doubly Robust CATE Estimator

## Mathematical Formula

For each action $a$, we seek to estimate the Conditional Average Treatment Effect (CATE) against a control $a=0$:
$$\tau_a(X) = E[Y(a) - Y(0) \mid X]$$

We use the standard Doubly Robust learner. For observation $i$:
1.  **Propensity Model**: $e_a(X_i) = P(A=a \mid X_i)$
2.  **Outcome Models**: $\mu_a(X_i) = E[Y \mid X_i, A=a]$ and $\mu_0(X_i) = E[Y \mid X_i, A=0]$

We construct the pseudo-outcome $\Gamma_{i,a}$ for treatment $a$:
$$\Gamma_{i,a} = \mu_a(X_i) + \frac{I(A_i=a)}{e_a(X_i)}(Y_i - \mu_a(X_i))$$
and for control $0$:
$$\Gamma_{i,0} = \mu_0(X_i) + \frac{I(A_i=0)}{e_0(X_i)}(Y_i - \mu_0(X_i))$$

The CATE pseudo-outcome is:
$$\tilde{Y}_{i,a} = \Gamma_{i,a} - \Gamma_{i,0}$$

We then fit a regressor (e.g., Ridge) $f_a(X)$ to predict $\tilde{Y}_{i,a}$.

## Assumptions
- **Unconfoundedness**: No unmeasured confounders.
- **Positivity (Overlap)**: $0 < P(A=a \mid X) < 1$ for all valid actions and contexts.
- **Consistency**: $Y_i = Y_i(A_i)$.

## Why the Old Implementation was Incorrect
The previous implementation computed $\tilde{Y}_{i,a}$ over the *entire* dataset $X_{all}$ (including rows where $A_i$ was neither $0$ nor $a$). For these unrelated rows, $I(A_i=a)=0$ and $I(A_i=0)=0$. Thus, the target $\tilde{Y}_{i,a}$ simply collapsed to the plugin estimator $\mu_a(X_i) - \mu_0(X_i)$ with no IPW correction. 

Because the Ridge regressor was trained on the entire population, the majority of the data points were supplying the exact predictions of the T-Learner. This heavily biased the final DR-Learner to just mimic the T-Learner, violating the intent of doubly robust subset weighting.

## Exact Corrected Implementation
The final regressor for action $a$ is now trained **exclusively on the subset $S_a = \{i \mid A_i \in \{0, a\}\}$**.
By restricting the training set, we ensure that every observation used to fit the regressor receives the appropriate IPW correction term.

## Limitations
- We use global propensity scores $e_a(X)$ over all actions rather than conditional scores within $\{0, a\}$. Since treatment assignment is uniform random in the logging policy, this is mathematically equivalent.
- We do not use cross-fitting (sample splitting) for the nuisance parameters, which may lead to slight overfitting in finite samples.
