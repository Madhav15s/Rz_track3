import unittest
import uuid
import time
from backend.app.razorpay.adapter import RazorpayTestAdapter, OutcomeLedger
from backend.app.policy.economic_policy import EconomicPolicyOptimizer, DeterministicPolicyGovernor, ACTION_CATALOG

# We mock the causal estimator for the E2E since we don't want to load a trained RandomForest inside a fast unit test.
class MockSupportAwareCausalPolicy:
    def get_best_action(self, context, model_overrides=None):
        # Suppose the causal model predicts Action 1 has 15% uplift, highly supported.
        return {
            "recommended_action": 1,
            "estimated_uplift": 0.15,
            "support": 0.85,
            "fallback_triggered": False,
            "expected_incremental_value_paise": int(context['amount_paise'] * 0.15) - 500
        }

class TestEndToEndPipeline(unittest.TestCase):
    def test_full_synthetic_pipeline(self):
        # 1. Synthetic Failed Payment Context
        case_id = "case_" + uuid.uuid4().hex[:8]
        context = {
            "case_id": case_id,
            "amount_paise": 100000,
            "customer_value_band": "high",
            "historical_payment_success_rate": 0.9,
            "time_since_failure_minutes": 15
        }
        
        # 2. Frozen Causal Policy (Mocked)
        causal_policy = MockSupportAwareCausalPolicy()
        causal_decision = causal_policy.get_best_action(context)
        
        self.assertEqual(causal_decision["recommended_action"], 1)
        
        # 3. Deterministic Policy Governor
        governor = DeterministicPolicyGovernor()
        
        # Governor assesses the proposal
        approval = governor.evaluate(context, causal_decision["recommended_action"])
        self.assertEqual(approval["status"], "APPROVED")
        
        # 4. Razorpay Adapter & Simulator
        ledger = OutcomeLedger()
        adapter = RazorpayTestAdapter(ledger)
        
        execution_result = adapter.execute_action(
            action_id=approval["action_id"],
            context=context,
            governor_approval=approval
        )
        
        self.assertEqual(execution_result["api_status"], "SUCCESS")
        
        # 5. Ledger State Transition
        status_after_exec = ledger.get_status(approval["correlation_id"])
        self.assertEqual(status_after_exec["status"], "PENDING_VERIFICATION")
        
        # 6. Webhook Verification
        provider_id = status_after_exec["provider_id"]
        webhook_id = "wh_" + uuid.uuid4().hex
        
        webhook_verification = ledger.verify_webhook(
            webhook_id=webhook_id,
            provider_id=provider_id,
            event_type="payment_link.paid",
            amount=context["amount_paise"]
        )
        
        self.assertEqual(webhook_verification["status"], "VERIFIED_RECOVERED")
        
        # 7. Final Outcome Ledger
        final_status = ledger.get_status(approval["correlation_id"])
        self.assertEqual(final_status["status"], "VERIFIED_RECOVERED")
        self.assertEqual(final_status["recovered_amount"], 100000)
        self.assertTrue(final_status["simulated"])

if __name__ == '__main__':
    unittest.main()
