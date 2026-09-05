# Final Demo Facts

This document strictly defines the terminology and claims permitted for the final Razorpay Buildathon submission. 

### What We CAN Claim
*   **Support-Aware Causal Inference:** We can claim the system isolates the *incremental* effect of interventions using causal estimators (T-Learner, DR-Learner) and strictly *abstains* when historical support is insufficient.
*   **Safety Over Prediction:** We can claim the system mathematically prefers abstaining (NO_ACTION) over hallucinating predictions in data-sparse regions.
*   **Deterministic Boundaries:** We can claim the LLM/Agent is structurally isolated from execution by a Deterministic Policy Governor.
*   **Webhook Integrity:** We can claim the system strictly verifies Razorpay webhook amounts against the initially requested order/link amount to prevent spoofed partial payments from being marked as verified recoveries.

### What We CANNOT Claim
*   **Production Deployment:** Do NOT claim this is running on live merchant data. It is a "Tested financial decisioning architecture for Razorpay test-mode/demo use."
*   **Solved Unmeasured Confounding:** Do NOT claim we solved hidden confounding. We claim that *abstention limits the damage* of unmeasured confounding by refusing to extrapolate.
*   **Real Razorpay Revenue:** All metrics are from synthetic generative environments simulating Razorpay transactional volume.
*   **Guaranteed Recovery:** Do NOT claim we guarantee payment recovery. We optimize expected value.

### Exact Terminology to Use
*   Instead of "The AI decides", use **"The Causal layer estimates, the Governor decides."**
*   Instead of "It makes predictions", use **"It estimates counterfactuals."**
*   Instead of "Razorpay integration", use **"Razorpay Test Mode / Simulator Integration."**
*   Instead of "Predicting who will pay", use **"Isolating the incremental effect of an intervention."**

### Razorpay Integration Details
*   The system executes actions exclusively via the Razorpay Python SDK using Test Mode credentials.
*   It utilizes `payment_link.create` and `order.create`.
*   It binds system state securely using `reference_id` or `receipt` as idempotency correlation IDs.
*   It securely ingests `payment_link.paid` and `order.paid` webhooks to drive an immutable outcome ledger.
