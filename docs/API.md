# CausalRecover API Reference

The Dashboard UI communicates exclusively with these read-only and strict-mutation endpoints to prevent LLM oracle leakage and bypasses.

## Endpoints

### `GET /api/overview`
Returns the canonical benchmark and macro operational metrics (Gross vs Incremental recovery, Abstentions, Policy Violations).
- **Source of truth:** `evaluation/CANONICAL_BENCHMARK.md`

### `GET /api/cases`
Returns a list of failed payment cases eligible for causal recovery.
- **Fields:** `case_id`, `amount_paise`, `failure_code`, `engagement_score`, etc.

### `GET /api/cases/{case_id}`
Returns details for a specific failed payment.

### `GET /api/cases/{case_id}/decision`
Returns the Causal Model's analysis of the counterfactuals for the case.
- **Fields:** `candidate_actions` (with Uplift, Support, Confidence, Value), `recommended_action`, `governor_status`, `explanation`.
- **Security:** Hides ground-truth oracle variables.

### `POST /api/cases/{case_id}/execute`
Initiates the recommended recovery action.
- **Payload:** `{"action_id": int}`
- **Security:** Always passes through the deterministic Policy Governor and Razorpay Adapter before mutating. Returns a `correlation_id`.

### `GET /api/incidents`
Returns active macro incidents (e.g., UPI Degradation) which affect the `context` passed to the causal models.

### `GET /api/audit`
Returns a chronologically ordered array of system events spanning the Causal Analysis, Governor Checks, API dispatch, and Webhook verification.

### `GET /api/evaluation`
Returns the raw Markdown string of the frozen Canonical Benchmark for the Evaluation view.
