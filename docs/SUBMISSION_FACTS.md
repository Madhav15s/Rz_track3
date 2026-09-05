# Final Submission Facts

This document serves as the canonical source for copying and pasting required fields into the Buildathon submission form.

### Project Name
CausalRecover

### Project Objective
To maximize net incremental revenue from failed payments using a support-aware causal AI decision engine, isolated by a deterministic policy governor and executed via Razorpay.

### GitHub URL
https://github.com/Madhav15s/Rz_track3

### Pitch Video Placeholder
[Insert YouTube / Drive Link Here]

### Build Challenges
1. **The Causal vs Predictive Gap:** Standard predictive ML ("Who will pay?") led to massive wasted intervention budgets on customers who would have recovered naturally. We had to implement heterogeneous treatment effect estimators (T-Learners / Doubly-Robust) to isolate the *marginal* effect of our actions.
2. **The Extrapolation Danger:** Causal ML models confidently hallucinated high uplift in data-sparse regions. We solved this by building a "Support-Aware" layer that mathematically calculates historical overlap and forcefully abstains when confidence is low.
3. **Execution Safety Boundaries:** Ensuring an autonomous AI didn't violate business rules or get manipulated by spoofed webhooks required building a strict Deterministic Policy Governor and an immutable, amount-verifying outcome ledger on top of the Razorpay SDK.
