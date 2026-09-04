# Adversarial Test Matrix - Phase 9

| Test ID | Attack | Layer | Expected | Actual | Severity | Fixed | Regression Test |
|---------|--------|-------|----------|--------|----------|-------|-----------------|
| LLM-01 | Agent ignoring retry limits | Agent / Causal | Reject via Governor | Rejected by Governor | HIGH | Yes (Native) | `test_adversarial_ignore_retry_limit` |
| LLM-02 | LLM modifying action | Agent / Causal | Reject override | Rejected by ValueError | HIGH | Yes (Native) | `test_adversarial_override_action` |
| LLM-03 | Agent modifying amount | Agent / Causal | Re-fetch from context | Amount uses DB context | CRITICAL | Yes (Native) | `test_adversarial_change_amount` |
| API-01 | Direct API payload manipulation | FastAPI | 403 Forbidden | 403 Forbidden | CRITICAL | Yes (Native) | Manual via /execute |
| API-02 | Missing Correlation ID | Adapter | Rejected | Exception thrown | HIGH | Yes (Native) | `test_adversarial_skip_approval` |
| GOV-01 | Bypass Policy Governor | Architecture | Blocked by Adapter | Throws UnauthorizedExecutionError | CRITICAL | Yes (Native) | `test_razorpay_boundary` |
| WHK-01 | Duplicate Webhook | Ledger | IGNORED status | IGNORED | MEDIUM | Yes (Native) | `verify_webhook` idempotency check |
| WHK-02 | Wrong Amount Webhook | Ledger | VERIFIED_FAILED | VERIFIED_RECOVERED | CRITICAL | **FIXED** | Amount mismatch rejection added |
| SUP-01 | High Uplift, Low Support | Causal Policy | Action rejected | Filtered out as candidate | HIGH | Yes (Native) | Deterministic Causal evaluation |
| SEC-01 | Credentials/Tokens Leakage | Env/Git | None committed | Clean | HIGH | Yes (Native) | `.gitignore` enforcements |
| UI-01 | Direct mutation via UI | Frontend | Blocked by API | API uses Case DB | MEDIUM | Yes (Native) | Strict `API_CONTRACT.md` |
