# Video Shot List

**Target Duration:** 4:30 – 4:50

### Scene 1: Introduction & Overview
*   **Timestamp:** 0:00 - 0:30
*   **Screen:** Executive Overview (`/`)
*   **Action:** Pan across the Gross vs Net Incremental Revenue charts.
*   **Highlight:** The massive gap between Gross Recovery and Net Incremental Recovery.
*   **Narration Purpose:** Hook the audience. Explain that failed payments aren't totally lost, and predicting "who will pay" wastes money on those who would recover naturally. We need *causal* recovery.

### Scene 2: The Decision Console
*   **Timestamp:** 0:30 - 1:15
*   **Screen:** Decision Console (`/cases`) -> Select `CASE_A_POS_UPLIFT`
*   **Action:** Click into Case A. Show the Candidate Actions matrix.
*   **Highlight:** Hover over the estimated uplift and the expected economic value (₹17,870). 
*   **Narration Purpose:** Show how the T-Learner isolates the *incremental* effect of `RETRY_LATER` and translates it into an economic decision.

### Scene 3: The Support-Aware Differentiator
*   **Timestamp:** 1:15 - 2:00
*   **Screen:** Decision Console (`/cases`) -> Select `CASE_C_OUT_OF_SUPPORT`
*   **Action:** Show the Candidate Actions matrix where `ALTERNATE_METHOD` is flagged.
*   **Highlight:** Highlight the +45% estimated uplift but 1% (0.01) Support. Point to the `ABSTAINED` status.
*   **Narration Purpose:** This is the killer feature. Standard ML would aggressively spend money here. CausalRecover recognizes it lacks historical overlap for this action and safely abstains, falling back to NO_ACTION.

### Scene 4: The Deterministic Governor
*   **Timestamp:** 2:00 - 2:30
*   **Screen:** Decision Console (`/cases`) -> Select `CASE_D_POLICY_REJECT`
*   **Action:** Look at the bottom decision panel.
*   **Highlight:** The Causal ML recommended `RETRY_NOW`, but the Governor status is `POLICY_REJECTED` (Max retry velocity exceeded).
*   **Narration Purpose:** Prove that the LLM and the ML are not the final authority. A deterministic, hard-coded policy governor stands between the AI and Razorpay.

### Scene 5: Execution & Razorpay Integration
*   **Timestamp:** 2:30 - 3:15
*   **Screen:** Execution Log (`/execution`) & Audit Trail (`/audit`)
*   **Action:** Show the flow from `PENDING_VERIFICATION` to `VERIFIED_RECOVERED` for `CASE_E_VERIFIED`.
*   **Highlight:** The strict webhook verification flow.
*   **Narration Purpose:** Explain that execution happens via Razorpay Test Mode SDK (Payment Links / Orders). Mention the critical security fix: the system enforces strict amount-integrity checks on webhooks to prevent spoofing.

### Scene 6: Scientific Evaluation
*   **Timestamp:** 3:15 - 4:00
*   **Screen:** Evaluation (`/evaluation`)
*   **Action:** Scroll through the Five-Regime Benchmark tables.
*   **Highlight:** The RCT regime table, specifically Net Incremental Revenue (₹92.9M) and Oracle Capture (71.5%).
*   **Narration Purpose:** We didn't just guess; we built a generative structural causal model to simulate 5 hostile data environments (bias, confounding) to mathematically prove the superiority of support-aware policies.

### Scene 7: Conclusion
*   **Timestamp:** 4:00 - 4:30
*   **Screen:** Executive Overview / Architecture Diagram
*   **Action:** Show the Safety boundary chart.
*   **Highlight:** Zero policy violations.
*   **Narration Purpose:** Conclude with the core thesis: CausalRecover doesn't just predict; it acts optimally, safely, and verifiably.
