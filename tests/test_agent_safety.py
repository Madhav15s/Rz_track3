import unittest
from backend.app.agent.investigator import AgentOrchestrator, AgentRecommendation
from backend.app.policy.economic_policy import DeterministicPolicyGovernor
from backend.app.razorpay.adapter import RazorpayTestAdapter, OutcomeLedger, UnauthorizedExecutionError

class MockCausalPolicy:
    def get_best_action(self, context):
        return {
            "recommended_action": 1,
            "estimated_uplift": 0.15,
            "expected_incremental_value_paise": 5000,
            "confidence": "HIGH"
        }

class TestAgentSafety(unittest.TestCase):
    def setUp(self):
        self.ledger = OutcomeLedger()
        self.adapter = RazorpayTestAdapter(self.ledger)
        self.governor = DeterministicPolicyGovernor()
        self.causal = MockCausalPolicy()
        self.agent = AgentOrchestrator(self.causal, self.governor, self.adapter)
        
        self.context = {
            "case_id": "test_case_1",
            "amount_paise": 10000,
            "retries_attempted": 0
        }

    def test_adversarial_override_action(self):
        # The agent generates a valid recommendation
        rec = self.agent.generate_recommendation(self.context, "Looks good.")
        
        # The adversarial LLM modifies the output to force a human escalation (Action 5)
        rec.recommended_action = 5
        
        with self.assertRaisesRegex(ValueError, "Agent attempted to override Causal Policy recommendation."):
            self.agent.execute_recommendation(self.context, rec)

    def test_adversarial_skip_approval(self):
        # LLM tries to call adapter directly without governor approval
        rec = self.agent.generate_recommendation(self.context, "Skipping approval.")
        
        fake_approval = {
            "status": "APPROVED", # Forged
            "action_id": rec.recommended_action,
            "case_id": self.context["case_id"]
        }
        
        # Will fail because correlation_id and idempotency_key are missing/invalid from forgery
        with self.assertRaises(ValueError):
            self.adapter.execute_action(rec.recommended_action, self.context, fake_approval)
            
    def test_adversarial_ignore_retry_limit(self):
        rec = self.agent.generate_recommendation(self.context, "retrying anyway")
        
        # Context shows max retries exceeded
        bad_context = self.context.copy()
        bad_context["retries_attempted"] = 5
        
        with self.assertRaisesRegex(ValueError, "Agent recommendation rejected by Policy Governor"):
            self.agent.execute_recommendation(bad_context, rec)
            
    def test_adversarial_change_amount(self):
        # LLM tells the user it changed the amount
        rec = self.agent.generate_recommendation(self.context, "Changing amount to 50.")
        
        # Even if the LLM says it changed the amount, the orchestrator passes the immutable `context` to the adapter.
        # Let's ensure the adapter uses context['amount_paise'] and it hasn't changed.
        res = self.agent.execute_recommendation(self.context, rec)
        self.assertEqual(res["api_status"], "SUCCESS")
        
        # If the LLM tries to forge a new context
        forged_context = self.context.copy()
        forged_context["amount_paise"] = 50000000 # Way over governor limit
        
        with self.assertRaisesRegex(ValueError, "Agent recommendation rejected by Policy Governor"):
            self.agent.execute_recommendation(forged_context, rec)

if __name__ == '__main__':
    unittest.main()
