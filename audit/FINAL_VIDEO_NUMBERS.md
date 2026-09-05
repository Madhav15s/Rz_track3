# Final Video Numbers

The following numbers represent the exact, canonical metrics for the **Support-Aware Causal Policy** under the **RCT (Randomized Control Trial)** synthetic evaluation regime.

These numbers MUST be used if metrics are verbally cited in the video or pitch. Do not use numbers from observational regimes unless specifically discussing the failure modes of standard models under bias.

**Regime:** Synthetic RCT (`benchmark_rct_n10k`)

*   **Gross Recovery:** ₹295,648,417
*   **Natural Recovery (Baseline):** ₹202,060,897
*   **Incremental Recovery:** ₹93,587,520
*   **Net Incremental Revenue:** ₹92,935,770
*   **Policy Regret:** ₹35,838,381
*   **Oracle Capture:** 71.50%
*   **Abstention Rate (RCT):** 0.00% (Since RCT ensures perfect overlap/support across all interventions)
*   **Abstention Rate (Severe Positivity):** *If you mention abstention in biased data, refer to the SEVERE_POSITIVITY regime where the model formally abstains (e.g. 0.15% - 2.0% depending on exact seed constraint, preventing unsafe extrapolation).*

**Safety Boundaries Verified:**
*   Governor bypasses: 0
*   Unauthorized Executions: 0
*   Webhook Amount Spoofing: 0 (Mitigated)
