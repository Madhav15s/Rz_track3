import unittest
import uuid
import time
from backend.app.razorpay.adapter import RazorpayTestAdapter, OutcomeLedger, UnauthorizedExecutionError

class TestRazorpayBoundary(unittest.TestCase):
    def setUp(self):
        self.ledger = OutcomeLedger()
        self.adapter = RazorpayTestAdapter(self.ledger)
        self.case_id = "test_case_123"
        self.amount = 50000
        self.context = {"case_id": self.case_id, "amount_paise": self.amount}
        self.correlation_id = "corr_" + uuid.uuid4().hex
        self.idempotency_key = "idem_" + uuid.uuid4().hex
        
        self.valid_approval = {
            "status": "APPROVED",
            "action_id": 1,
            "case_id": self.case_id,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key
        }

    def test_01_valid_approved_execution(self):
        res = self.adapter.execute_action(1, self.context, self.valid_approval)
        self.assertEqual(res["api_status"], "SUCCESS")
        
        # Verify ledger state
        status = self.ledger.get_status(self.correlation_id)
        self.assertEqual(status["status"], "PENDING_VERIFICATION")

    def test_02_governor_rejection(self):
        rejected_approval = self.valid_approval.copy()
        rejected_approval["status"] = "POLICY_REJECTED"
        
        with self.assertRaises(UnauthorizedExecutionError):
            self.adapter.execute_action(1, self.context, rejected_approval)

    def test_04_duplicate_request_idempotency(self):
        res1 = self.adapter.execute_action(1, self.context, self.valid_approval)
        res2 = self.adapter.execute_action(1, self.context, self.valid_approval)
        
        self.assertEqual(res1["provider_id"], res2["provider_id"])
        self.assertEqual(len(self.adapter.idempotency_cache), 1)

    def test_05_duplicate_webhook(self):
        self.adapter.execute_action(1, self.context, self.valid_approval)
        status = self.ledger.get_status(self.correlation_id)
        provider_id = status["provider_id"]
        
        webhook_id = "wh_" + uuid.uuid4().hex
        wh_res1 = self.ledger.verify_webhook(webhook_id, provider_id, "payment_link.paid", self.amount)
        self.assertEqual(wh_res1["status"], "VERIFIED_RECOVERED")
        
        wh_res2 = self.ledger.verify_webhook(webhook_id, provider_id, "payment_link.paid", self.amount)
        self.assertEqual(wh_res2["status"], "IGNORED")
        self.assertEqual(wh_res2["reason"], "DUPLICATE_WEBHOOK")

    def test_06_out_of_order_webhook(self):
        # Webhook arrives for unknown provider_id
        wh_res = self.ledger.verify_webhook("wh_123", "unknown_provider", "payment_link.paid", 100)
        self.assertEqual(wh_res["status"], "UNKNOWN")
        self.assertEqual(wh_res["reason"], "PROVIDER_ID_NOT_FOUND")

    def test_07_fake_success(self):
        self.adapter.execute_action(1, self.context, self.valid_approval)
        status = self.ledger.get_status(self.correlation_id)
        provider_id = status["provider_id"]
        
        wh_res = self.ledger.verify_webhook("wh_fake", provider_id, "some_fake_event", self.amount)
        self.assertEqual(wh_res["status"], "UNKNOWN_EVENT")
        
        # Verify it didn't update to RECOVERED
        self.assertEqual(self.ledger.get_status(self.correlation_id)["status"], "PENDING_VERIFICATION")

    def test_10_unknown_payment_state(self):
        self.adapter.execute_action(1, self.context, self.valid_approval)
        status = self.ledger.get_status(self.correlation_id)
        self.assertEqual(status["status"], "PENDING_VERIFICATION")
        # Ensure it remains pending until explicit verification

    def test_12_unauthorized_mutation_action_mismatch(self):
        invalid_approval = self.valid_approval.copy()
        # Governor approved Action 1, but LLM tries to execute Action 2
        with self.assertRaises(UnauthorizedExecutionError):
            self.adapter.execute_action(2, self.context, invalid_approval)

    def test_12_unauthorized_mutation_case_mismatch(self):
        invalid_approval = self.valid_approval.copy()
        invalid_approval["case_id"] = "different_case"
        with self.assertRaises(UnauthorizedExecutionError):
            self.adapter.execute_action(1, self.context, invalid_approval)

if __name__ == '__main__':
    unittest.main()
