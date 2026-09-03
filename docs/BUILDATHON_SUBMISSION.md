# CausalRecover - Razorpay AI Buildathon 2026 Submission

## 1. Project Name & Track
**Project Name**: CausalRecover  
**Track**: Track 03 — AI Revenue Recovery  
**Tagline**: "Don't predict who will pay. Predict what causes them to pay."

## 2. What it solves
Current revenue recovery systems, including leading competitor patterns, typically optimize for *gross recovery* (predicting the probability a customer will pay if intervened upon). This leads to wasted interventions on customers who would have naturally recovered anyway, and causes potentially harmful friction (e.g., retrying an exhausted payment method causing a bank freeze).

CausalRecover solves this by evaluating **Heterogeneous Treatment Effects**. It explicitly predicts the *incremental* probability of recovery attributable solely to the action. It then models the economic constraints (risk and friction) to maximize **Expected Net Incremental Value**.

## 3. Architecture Summary
The system separates estimation from execution across 8 layers:
1. **Observation**: Detects failures and extracts observables.
2. **Causal Intelligence**: Employs T-Learners and Doubly Robust estimators to estimate $P(Y \mid do(A=a), X) - P(Y \mid do(A=0), X)$.
3. **Economic Decision**: Transforms causal uplift into expected value (Amount $\times$ Uplift - Intervention Costs).
4. **Safety Policy**: A deterministic Governor overriding unauthorized actions (e.g., retrying a Hard Decline).
5. **Execution**: Razorpay Test-Mode Adapter.
6. **Verification**: Simulated Webhook Ledger.
7. **Measurement & Learning**: Evaluates offline using Inverse Propensity Weighting (IPW).

## 4. AI Usage
- **Causal ML Models (SciKit-Learn)**: Train custom estimators to predict individualized treatment uplift.
- **LLM Reasoning (Agent Explainer)**: Synthesizes the quantitative causal evidence and the deterministic policy into an explainable, human-readable audit trail. Crucially, the LLM does *not* have direct money-moving capabilities.

## 5. Razorpay Integration
The execution layer wraps the Razorpay Python SDK and bounds MCP server capabilities. We target official Test-Mode APIs (creating Orders or Payment Links based on the action selected). If API credentials are not provided, it falls back to a deterministic simulation gateway to demonstrate the workflow. 

## 6. Measured Results
Evaluated on a strictly isolated test set, comparing policies:
- **Baseline (Fixed Rules)**: High intervention rate, moderate incremental value.
- **Causal Policy (T-Learner/Doubly Robust)**: Reduced interventions by targeting only those with positive causal uplift, generating significantly higher Net Incremental Revenue.
- **Oracle (Theoretical Upper Bound)**: Our system closes the gap between standard models and the perfect Oracle by ignoring customers who naturally recover.

## 7. What broke and how we fixed it
During evaluation, our initial pandas DataFrame merging logic repeatedly joined the Oracle Potential Outcomes onto the Features matrix, creating duplicate columns and producing heavily biased sum values (pandas Series collisions). We fixed this by aggressively dropping duplicate ID columns and ensuring the testing harness was completely structurally isolated from the Oracle evaluation pipeline, strictly preventing data leakage into the observable test space.

## 8. Why this is different
We penalize actions where natural recovery is already high. If a customer has a 90% chance of paying with No Action, and a 94% chance of paying with a Retry, we observe only a 4% causal uplift. If the intervention cost exceeds that 4% expected value, we rigorously **Abstain**. Most systems would eagerly retry the 94% customer just to inflate their "gross recovered" metrics. We optimize for truth.
