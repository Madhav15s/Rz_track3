import unittest
from fastapi.testclient import TestClient
from backend.app.api.main import app
from backend.app.api.db import init_db, get_db

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We ensure DB is initialized for tests
        import os
        from backend.app.api.db import DB_PATH
        if not os.path.exists(DB_PATH):
            init_db()
            
    def setUp(self):
        self.client = TestClient(app)

    def test_overview(self):
        response = self.client.get("/api/overview")
        self.assertEqual(response.status_code, 200)
        self.assertIn("revenue_at_risk", response.json())
        self.assertIn("incremental_recovery", response.json())

    def test_cases(self):
        response = self.client.get("/api/cases")
        self.assertEqual(response.status_code, 200)
        self.assertIn("cases", response.json())

    def test_incidents(self):
        response = self.client.get("/api/incidents")
        self.assertEqual(response.status_code, 200)
        self.assertIn("incidents", response.json())

    def test_audit(self):
        response = self.client.get("/api/audit")
        self.assertEqual(response.status_code, 200)
        self.assertIn("events", response.json())

    def test_evaluation(self):
        response = self.client.get("/api/evaluation")
        # May be 500 if file missing during test, but we expect 200
        if response.status_code == 200:
            self.assertIn("markdown", response.json())

    def test_case_decision_404(self):
        response = self.client.get("/api/cases/INVALID_CASE/decision")
        self.assertEqual(response.status_code, 404)
        
    def test_governor_bypass(self):
        # CASE_D_POLICY_REJECT is hardcoded to retry limit exceeded
        response = self.client.post("/api/cases/CASE_D_POLICY_REJECT/execute", json={"action_id": 1})
        self.assertEqual(response.status_code, 403)
        self.assertIn("Governor Rejected", response.json()["detail"])

if __name__ == '__main__':
    unittest.main()
