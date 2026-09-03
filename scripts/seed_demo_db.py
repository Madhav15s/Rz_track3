import sqlite3
import time
import uuid
from backend.app.api.db import get_db, init_db, log_audit_event

def seed_demo_data():
    init_db()
    conn = get_db()
    c = conn.cursor()
    
    # Clear existing demo data
    c.execute("DELETE FROM cases WHERE is_demo = 1")
    c.execute("DELETE FROM incidents")
    c.execute("DELETE FROM executions")
    c.execute("DELETE FROM audit_events")
    
    # Seed Incidents
    incidents = [
        {
            "id": "INC-UPI-001",
            "type": "BANK / UPI DEGRADATION",
            "severity": "HIGH",
            "start_time": "2026-09-04T09:00:00Z",
            "duration_minutes": 45,
            "affected_payment_method": "UPI",
            "affected_bank": "HDFC",
            "transactions_affected": 12450,
            "revenue_exposed_paise": 450000000,
            "status": "ACTIVE"
        }
    ]
    for inc in incidents:
        c.execute('''
            INSERT INTO incidents (id, type, severity, start_time, duration_minutes, affected_payment_method, affected_bank, transactions_affected, revenue_exposed_paise, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inc["id"], inc["type"], inc["severity"], inc["start_time"], inc["duration_minutes"], inc["affected_payment_method"], inc["affected_bank"], inc["transactions_affected"], inc["revenue_exposed_paise"], inc["status"]))
        
    # Seed Cases (Demo Mode Cases requested by user)
    cases = [
        # CASE A: Positive uplift
        ("CASE_A_POS_UPLIFT", 150000, "UPI", "HDFC", "TIMED_OUT", 0, 5, 0.9, 0.8, "high", 1),
        # CASE B: Natural recovery trap (High historical success, will likely recover anyway)
        ("CASE_B_NATURAL_TRAP", 50000, "CARD", "ICICI", "INSUFFICIENT_FUNDS", 0, 10, 0.99, 0.9, "high", 1),
        # CASE C: Out-of-support counterfactual (Low engagement, weird bank, low success rate)
        ("CASE_C_OUT_OF_SUPPORT", 1000000, "NETBANKING", "UNKNOWN_BANK", "BANK_DECLINE", 0, 60, 0.1, 0.1, "low", 1),
        # CASE D: Policy rejection (Retries exceeded)
        ("CASE_D_POLICY_REJECT", 250000, "UPI", "SBI", "TIMED_OUT", 4, 120, 0.5, 0.5, "medium", 1),
        # CASE E: Verified Razorpay/simulated recovery
        ("CASE_E_VERIFIED", 75000, "CARD", "HDFC", "TIMED_OUT", 0, 15, 0.8, 0.7, "medium", 1)
    ]
    
    c.executemany('''
        INSERT INTO cases (case_id, amount_paise, payment_method, bank, failure_code, retries_attempted, time_since_failure_minutes, historical_payment_success_rate, engagement_score, customer_value_band, is_demo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', cases)
    
    # Pre-seed CASE_E execution to show a VERIFIED state
    corr_id = f"corr_CASE_E_{int(time.time()*1000)}"
    c.execute('''
        INSERT INTO executions (correlation_id, case_id, action_id, provider_id, status, recovered_amount, simulated, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (corr_id, "CASE_E_VERIFIED", 2, "sim_req_12345", "VERIFIED_RECOVERED", 75000, 1, time.time() - 3600))
    
    conn.commit()
    conn.close()
    
    log_audit_event("CASE_E_VERIFIED", corr_id, "PAYMENT_FAILED", "Initial payment failed via CARD.")
    log_audit_event("CASE_E_VERIFIED", corr_id, "CAUSAL_ANALYSIS", "Causal model evaluated. Selected Action 2 (RETRY_LATER).")
    log_audit_event("CASE_E_VERIFIED", corr_id, "GOVERNOR_APPROVED", "Governor approved Action 2.")
    log_audit_event("CASE_E_VERIFIED", corr_id, "EXECUTION_PENDING", "Razorpay Simulated Request Sent.")
    log_audit_event("CASE_E_VERIFIED", corr_id, "WEBHOOK_RECEIVED", "Webhook order.paid received.")
    log_audit_event("CASE_E_VERIFIED", corr_id, "VERIFIED_RECOVERED", "Recovery verified.")

if __name__ == "__main__":
    seed_demo_data()
    print("Demo data seeded.")
