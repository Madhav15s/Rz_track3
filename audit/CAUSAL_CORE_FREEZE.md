# CAUSAL CORE FREEZE

## 1. Final Thesis
**"Support-aware causal decisioning: estimate incremental intervention effects where historical evidence supports the counterfactual, and abstain when it does not."**

## 2. Final Benchmark
The definitive performance of the frozen architecture is recorded in `evaluation/CANONICAL_BENCHMARK.md`. This benchmark evaluates the pipeline across 5 regimes (RCT, Mild Observational, Strong Observational, Severe Positivity, Unmeasured Confounding) spanning 5 distinct randomized seeds.

## 3. Known Limitations
- **Unmeasured Confounding:** The pipeline cannot perfectly unconfound data if the historical treatment assignment policy relied on variables omitted from the model. Support-awareness mitigates the financial damage, but estimation bias remains.
- **Support-Driven Timidity:** By enforcing a strict support threshold, the model is inherently timid. If a highly effective but historically under-explored action could benefit a new segment, the model will refuse to explore it. A separate Multi-Armed Bandit (MAB) exploration layer would be required to actively gather missing support.
- **Miscalibration in the Tails:** We do not claim perfect counterfactual calibration. Unconstrained causal estimators inherently hallucinate when extrapolating (predicting >40% uplift when true uplift is ~18.82%). The system handles this via support-aware abstention, not by fixing the underlying calibration curve.
- **Static Costs:** The economic optimizer relies on fixed scalar definitions of cost, friction, and risk. If these macro-economic variables change dynamically, the policy will optimize for outdated definitions.

## 4. Known Assumptions
- **Strong Ignorability (SITA):** Assumes no unmeasured confounders for the true causal effect to be identifiable.
- **SUTVA (Stable Unit Treatment Value Assumption):** Assumes no interference between customers. One customer's intervention does not affect another's recovery probability.
- **Linear Utility:** Assumes the financial value of an intervention is linearly equal to `(Amount * Incremental Uplift) - Costs`.

## 5. Final Model Versions
The official `SupportAwareCausalPolicy` is constructed using:
- **Causal Estimator:** `TLearner` (6 independent `LogisticRegression(max_iter=1000)` classifiers, one per action, predicting $Y_a \sim X$).
- **Support / Propensity Model:** `RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)` predicting $P(A=a|X)$.

## 6. Final Threshold
- **`min_support = 0.05` (5%)**
- Chosen purely on a 20% validation split of the training data from the Strong Observational regime to balance intervention rate against epistemic safety.

## 7. Final Evaluation Seed Set
The canonical benchmark and all final scientific evaluations were rigorously tested across:
- **Seeds:** `[10, 20, 30, 40, 50]`

---
**STATUS: CAUSAL CORE FROZEN. NO FURTHER SCIENTIFIC MODIFICATIONS PERMITTED WITHOUT EXPLICIT UNFREEZE COMMAND.**
