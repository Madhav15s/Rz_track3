# Security Failure Postmortem

**PROBLEM**
Amount manipulation via Webhook Spoofing.

**WHAT BROKE**
The `verify_webhook` method in `OutcomeLedger` unconditionally accepted the payment amount sent by the webhook, setting the execution status to `VERIFIED_RECOVERED` without verifying that the returned amount equaled the initially expected amount requested by the causal model.

**WHY IT MATTERED**
An adversary could spoof or intercept a webhook, returning `amount: 1` instead of `10000`. The system would mark the 10000 case as fully recovered, resulting in catastrophic loss of unrecovered revenue and a false assertion of safety in the CausalRecover platform.

**ROOT CAUSE**
`OutcomeLedger.record_execution` only accepted `correlation_id`, `case_id`, `action_id`, `provider_id`, and `is_simulated`. It did not track the original expected amount requested. Consequently, the webhook validation step lacked the context required to authenticate amount integrity.

**FIX**
1. Added an `expected_amount: int` parameter to `OutcomeLedger.record_execution`.
2. Updated `RazorpayTestAdapter` to pass `expected_amount=amount` during execution.
3. Added a strict verification boundary in `verify_webhook` ensuring that `amount == execution.get("expected_amount")`. If the amount is mismatched, the ledger forcibly sets the status to `VERIFIED_FAILED` with the reason `AMOUNT_MISMATCH`.

**REGRESSION TEST**
Verified manually via interactive tests and by injecting mock requests to `verify_webhook`.

**RESULT AFTER FIX**
The system actively rejects amount mismatch attempts via webhooks, successfully preserving the integrity of the Verified Ledger.
