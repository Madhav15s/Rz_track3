# Buildathon Demo Runbook

This guide ensures a flawless, 3-minute pitch demonstrating the core value of CausalRecover: **Preventing hallucinated AI actions while maximizing incremental revenue.**

## Preparation
1. Start the API Server:
   `$env:PYTHONPATH="."; uvicorn backend.app.api.main:app --port 8000`
2. Start the Frontend:
   `cd frontend; npm run dev`

## The 3-Minute Script

### 1. The Value Proposition (Executive Overview)
- Navigate to **Executive Overview**.
- **Script:** "Most ML pipelines optimize for Gross Recovery, which is a trap. If someone was going to pay anyway, AI intervention just wastes money and adds friction. CausalRecover focuses purely on *Net Incremental Revenue*—the money we *wouldn't* have gotten without the intervention. As you can see, we generated ₹9.2M in true incremental value."

### 2. The Danger of Unconstrained Models (Decision Console)
- Navigate to **Decision Console** -> Select `CASE_D_POLICY_REJECT`
- **Script:** "Standard models hallucinate when given sparse data. Here, the raw Causal Model predicts massive uplift for `RETRY_NOW`. But notice the *Support* is too low, and the *Governor* steps in. Our deterministic safety layer rejects the hallucination (Max Retry Velocity Exceeded) and defaults to `NO_ACTION`. Policy Violations remain zero."

### 3. The Epistemic Safety Net (Decision Console)
- Select `CASE_C_OUT_OF_SUPPORT`
- **Script:** "Here's an out-of-support counterfactual. The model wants to use `ALTERNATE_METHOD` but the historical support is only 1%. The Support-Aware architecture actively abstains rather than extrapolating blindly. This simple threshold saved ₹4.8M in our severe positivity benchmarks."

### 4. The Happy Path (Decision Console -> Execution)
- Select `CASE_E_VERIFIED`
- **Script:** "Now let's look at a well-supported case. The model recommends `RETRY_LATER` with strong support and positive expected value. The Governor approves."
- Click **Execute**.
- **Script:** "The AI doesn't touch the database. It sends a request to the Razorpay Adapter (simulated/test mode). The Ledger records it as Pending until an authentic webhook verifies the recovery."
- Navigate to **Execution / Razorpay** to show the state transitions, ending in `VERIFIED RECOVERED`.

### 5. Proof of Rigor (Evaluation)
- Navigate to **Evaluation**.
- **Script:** "Our claims aren't based on a single cherry-picked run. This is our Canonical Benchmark across 5 distinct seeds and 5 confounding regimes, proving that Support-Aware Causal Policy is mathematically superior to naive propensity models."
