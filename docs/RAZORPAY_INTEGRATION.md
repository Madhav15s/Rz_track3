# RAZORPAY INTEGRATION PRE-FLIGHT

## Execution Architecture
The current execution architecture implements a strict boundary between the intelligence layer (Agent/Model) and the execution layer (Razorpay API).

**Flow:**
`CAUSAL POLICY -> ECONOMIC DECISION -> DETERMINISTIC POLICY GOVERNOR -> RAZORPAY ADAPTER -> SIMULATOR/TEST MODE -> WEBHOOK -> VERIFICATION -> OUTCOME LEDGER`

## Real vs Simulated Implementations

In `backend/app/razorpay/adapter.py`, the `RazorpayTestAdapter` dynamically determines the execution context based on provided credentials and action types:

- **REAL**: 
  - If `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are provided and the `razorpay` Python SDK is installed, the adapter executes real calls to the Razorpay Test API.
  - Action `1` (Retry Now) and Action `2` (Retry Later) create an actual Razorpay **Payment Link**.
  - Action `4` (Alternate Method) creates an actual Razorpay **Order**.

- **SIMULATED**:
  - If SDK/credentials are absent, or if the action does not map directly to a Razorpay API primitive (e.g., Action `5` Human Escalation, Action `0` Do Nothing), the adapter generates a deterministic simulated network response (`sim_req_<correlation_id>`).

- **HYBRID**:
  - The `OutcomeLedger` acts as a hybrid bridge. It records the API execution state, but enforces that **API call succeeded != Revenue Recovered**. Revenue is only marked recovered when the ledger's `verify_webhook` method successfully matches an authentic incoming Razorpay Webhook against the original `provider_id`.

## Security Boundaries & Agent Safety
The Causal Model and the LLM Agent **NEVER** get direct Razorpay mutation authority.

The `execute_action` method strictly enforces:
```python
def _verify_governor_approval(self, governor_approval: Dict[str, Any], action_id: int, case_id: str):
```
1. **Approval Status:** Execution aborts if `governor_approval['status'] != 'APPROVED'`.
2. **Action Forgery Protection:** Execution aborts if the requested `action_id` does not perfectly match the governor's approved `action_id`.
3. **Case Idempotency:** Execution aborts if the requested `case_id` does not match the governor's approved `case_id`.

## State Flow
Payments transition strictly through these states, recorded in the `OutcomeLedger`:
- `PROPOSED` (By the model/agent)
- `POLICY_REJECTED` / `APPROVED` (By the Governor)
- `PENDING_VERIFICATION` (Once executed via API)
- `VERIFIED_RECOVERED` (Only upon matching `payment_link.paid`, `order.paid` webhooks)
- `VERIFIED_FAILED` (Upon matching `payment.failed` webhooks)
- `UNKNOWN_EVENT` / `IGNORED` (Duplicate/unknown webhooks)
