# FINAL TECHNICAL AUDIT: CausalRecover

## AUDIT 1: REPOSITORY INVENTORY
**PHASE STATUS**
- Phase 1: Reconnaissance & Architecture (IMPLEMENTED)
- Phase 2: Synthetic World & Oracle (IMPLEMENTED)
- Phase 3: Baselines & Causal Models (IMPLEMENTED)
- Phase 4: Policy & Governor (IMPLEMENTED)
- Phase 5: Evaluation Harness (IMPLEMENTED)
- Phase 6: Razorpay Adapter (IMPLEMENTED)
- Phase 7: Agent / LLM Explanation Layer (PARTIAL - Explainer written, no active LLM yet)
- Phase 8: Dashboard (MISSING)
- Phase 9: Adversarial Tests (MISSING)
- Phase 10: Demo Mode / Submission (PARTIAL - Seed demo & Submission doc generated)

## AUDIT 2: DATA-LEAKAGE AUDIT
**STATUS:** STRUCTURAL LEAKAGE DETECTED
**Details:** `scripts/train_and_evaluate.py` line 124 calls `evaluate_policy_on_oracle(df_features_test_oracle, df_oracle, policy_fn)`. Inside that function, the features matrix is merged with the oracle potential outcomes matrix (`y_0` to `y_5`). The `policy_fn` is then invoked with `row.to_dict()` containing these hidden variables. Although the `ColumnTransformer` inside the causal models gracefully ignores `y_0`, the inference context structurally leaks the ground truth to any future agent/model logic. 
**Required Fix:** The evaluation harness must NEVER merge oracle columns into the `ctx` payload supplied to `policy_fn`.

## AUDIT 3: SYNTHETIC DATA-GENERATING PROCESS
**STATUS:** VERIFIED WORKING
**Details:** Analysed `simulator/generators/synthetic_data.py` logic. 
- Heterogeneous treatment effects are present (standard deviations are between 0.54 and 0.63).
- Positive and Negative effects are accurately simulated. Example: `action_1` (Immediate Retry) averages a -3.0% negative uplift and triggers a 21.6% negative effect rate overall (often harmful for insufficient funds), whereas `action_2` (Retry Later) produces +26.8% mean uplift. 
- Nonlinear effects are implemented using a valid structural logistic formulation based on interacting continuous latent features (e.g. `latent_payment_reliability` and `latent_liquidity`).

## AUDIT 4 & 11: ORACLE AUDIT
**STATUS:** WORKING BUT NEEDS HARDENING
**Details:** The Oracle produces true potential outcomes correctly, allowing for unbiased measurement of incremental policy value and regret. However, because of the structural leakage in Audit 2, the production policy execution context technically holds the Oracle values in memory. 

## AUDIT 5: TRAIN / VALIDATION / TEST AUDIT
**STATUS:** VERIFIED WORKING
**Details:** Customer ID level split is strictly implemented. `train_test_split_audit.py` confirmed 0 overlap across train, val, and test splits.

## AUDIT 6: TREATMENT ASSIGNMENT
**STATUS:** VERIFIED WORKING
**Details:** Assignments are simulated via randomized uniform exploration. Propensities (`propensity = 1.0 / len(eligible_actions)`) are properly logged in the dataset, satisfying the positivity assumption necessary for off-policy causal inference.

## AUDIT 7: T-LEARNER AUDIT
**STATUS:** VERIFIED WORKING
**Details:** 
- Model uses separate `LogisticRegression` pipelines for each treatment. 
- Target is the observed binary outcome.
- Computes `tau = mu_a(X) - mu_0(X)` cleanly.

## AUDIT 8: DOUBLY ROBUST AUDIT
**STATUS:** PARTIALLY CORRECT
**Details:** The implementation fits a Random Forest propensity model and logistic regression outcome models. It constructs the correct pseudo-outcome Gamma_a - Gamma_0 using Inverse Propensity Weighting. However, the final regressor (Ridge) is trained on `X_all`. For rows where A_i is neither 0 nor a, the IPW terms cancel to zero, leaving the target as simply mu_a(X_i) - mu_0(X_i). This incorrectly trains the DR learner to mimic the T-Learner on the subset of data that received unrelated treatments, failing to properly cross-fit or isolate the subset A_i in (0, a). 
**Required Fix:** Filter the training regression data to `(A_all == 0) | (A_all == a)` or apply cross-fitting.

## AUDIT 9: ECONOMIC POLICY AUDIT
**STATUS:** VERIFIED WORKING
**Details:** The policy computes `expected_incremental_value = (amount * uplift) - cost - friction - risk`. The deterministic governor is fully detached from the LLM, properly blocking forbidden actions (e.g., Hard Declines). Abstention works: actions default to `NO_ACTION` if net value is negative.

## AUDIT 10: EVALUATION AUDIT
**STATUS:** WORKING BUT NEEDS HARDENING
**Details:** Calculates true incremental revenue strictly via `true_uplift * amount` using the hidden potential outcomes. However, the metric generation must extract `y_0` cleanly without polluting the observation context (Audit 2). 

## AUDIT 13: REPEATED-SEED AUDIT
**STATUS:** VERIFIED WORKING
Evaluated across 5 random seeds (10, 20, 30, 40, 50).
The models consistently demonstrate a hierarchy where T-Learner and DR-Learner strictly outperform Fixed Dunning baselines on net incremental revenue across randomly seeded distributions.

## AUDIT 17: RAZORPAY ADAPTER AUDIT
**STATUS:** VERIFIED WORKING
**Details:** `backend/app/razorpay/adapter.py` correctly acts as a secure boundary. If `RAZORPAY_KEY_ID` exists, it hits official test-mode APIs (Payment Links / Orders). Otherwise, it simulates.

## FINAL AUDIT VERDICT

**VERDICT: WORKING BUT NEEDS HARDENING**

### REQUIRED FIXES BEFORE CONTINUING:
1. **Fix Structural Leakage in Evaluation**: Refactor `evaluate_policy_on_oracle` to look up Oracle variables independently using `case_id` rather than merging them into the feature dictionary passed to `policy_fn`.
2. **Fix Doubly Robust Regressor**: Constrain the DR-Learner's Ridge regressor fit to only the subset of data where the assigned action was `a` or `0`, rather than interpolating the T-Learner's baseline over all unrelated treatments.
