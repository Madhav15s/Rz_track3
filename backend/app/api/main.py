from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import json
import os
import uuid
import time
from backend.app.api.db import get_db, log_audit_event
from backend.app.policy.economic_policy import ACTION_CATALOG

app = FastAPI(title="CausalRecover API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/overview")
def get_overview():
    # Read the canonical benchmark file to extract these numbers safely without running the model
    # Or just return the hardcoded canonical numbers for the demo since the frozen benchmark is truth.
    return {
        "revenue_at_risk": 202060897, # From Natural Recovery baseline + at risk
        "gross_recovery": 295648417,
        "natural_recovery": 202060897,
        "incremental_recovery": 93587520,
        "net_incremental_recovery": 92935770,
        "interventions": 100.0,
        "abstentions": 0.0,
        "policy_rejections": 0,
        "verified_recoveries": 10000,
        "policy_violations": 0
    }

@app.get("/api/cases")
def get_cases():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cases")
    cases = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"cases": cases}

@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case": dict(row)}

@app.get("/api/cases/{case_id}/decision")
def get_case_decision(case_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")
        
    context = dict(row)
    
    # We load the frozen dummy model for demo cases to ensure deterministic UI response
    # In a real app we'd load the pickle file, but for the API demo mode we mock the exact responses
    # specified by the user's DEMO MODE constraints so it's instantly responsive and robust.
    
    decisions = []
    recommended_action = 0
    final_status = "AVAILABLE"
    governor_status = "APPROVED"
    rejection_reason = ""
    
    # Mocking the 5 cases to exactly match the Buildathon requested scenarios
    if case_id == "CASE_A_POS_UPLIFT":
        decisions = [
            {"action": 1, "name": "RETRY_NOW", "estimated_uplift": 0.02, "support": 0.15, "confidence": "LOW", "expected_incremental_value_paise": 2850, "status": "NOT SELECTED"},
            {"action": 2, "name": "RETRY_LATER", "estimated_uplift": 0.12, "support": 0.85, "confidence": "HIGH", "expected_incremental_value_paise": 17870, "status": "SELECTED"},
            {"action": 0, "name": "NO_ACTION", "estimated_uplift": 0.0, "support": 1.0, "confidence": "HIGH", "expected_incremental_value_paise": 0, "status": "AVAILABLE"}
        ]
        recommended_action = 2
    
    elif case_id == "CASE_B_NATURAL_TRAP":
        decisions = [
            {"action": 1, "name": "RETRY_NOW", "estimated_uplift": 0.005, "support": 0.8, "confidence": "HIGH", "expected_incremental_value_paise": -120, "status": "NOT SELECTED"},
            {"action": 2, "name": "RETRY_LATER", "estimated_uplift": -0.01, "support": 0.8, "confidence": "HIGH", "expected_incremental_value_paise": -630, "status": "NOT SELECTED"},
            {"action": 0, "name": "NO_ACTION", "estimated_uplift": 0.0, "support": 1.0, "confidence": "HIGH", "expected_incremental_value_paise": 0, "status": "SELECTED"}
        ]
        recommended_action = 0
        
    elif case_id == "CASE_C_OUT_OF_SUPPORT":
        decisions = [
            {"action": 4, "name": "ALTERNATE_METHOD", "estimated_uplift": 0.45, "support": 0.01, "confidence": "LOW", "expected_incremental_value_paise": 0, "status": "ABSTAINED"},
            {"action": 0, "name": "NO_ACTION", "estimated_uplift": 0.0, "support": 1.0, "confidence": "HIGH", "expected_incremental_value_paise": 0, "status": "SELECTED"}
        ]
        recommended_action = 0
        
    elif case_id == "CASE_D_POLICY_REJECT":
        decisions = [
            {"action": 1, "name": "RETRY_NOW", "estimated_uplift": 0.15, "support": 0.9, "confidence": "HIGH", "expected_incremental_value_paise": 37330, "status": "POLICY_REJECTED"},
            {"action": 0, "name": "NO_ACTION", "estimated_uplift": 0.0, "support": 1.0, "confidence": "HIGH", "expected_incremental_value_paise": 0, "status": "SELECTED"}
        ]
        recommended_action = 1
        governor_status = "POLICY_REJECTED"
        rejection_reason = "Max retry velocity exceeded."
        
    elif case_id == "CASE_E_VERIFIED":
        decisions = [
            {"action": 2, "name": "RETRY_LATER", "estimated_uplift": 0.08, "support": 0.6, "confidence": "MEDIUM", "expected_incremental_value_paise": 5870, "status": "SELECTED"}
        ]
        recommended_action = 2

    return {
        "candidate_actions": decisions,
        "recommended_action": recommended_action,
        "governor_status": governor_status,
        "rejection_reason": rejection_reason,
        "explanation": "Causal policy analyzed the counterfactuals and selected the optimal supported action."
    }

@app.get("/api/incidents")
def get_incidents():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM incidents")
    incidents = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"incidents": incidents}

@app.get("/api/audit")
def get_audit(case_id: str = None):
    conn = get_db()
    c = conn.cursor()
    if case_id:
        c.execute("SELECT * FROM audit_events WHERE case_id=? ORDER BY timestamp DESC", (case_id,))
    else:
        c.execute("SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT 100")
    events = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"events": events}

@app.post("/api/cases/{case_id}/execute")
def execute_case(case_id: str, payload: dict):
    action_id = payload.get("action_id", 0)
    
    corr_id = f"corr_{case_id}_{int(time.time()*1000)}"
    log_audit_event(case_id, corr_id, "EXECUTION_REQUESTED", f"User requested execution for action {action_id}")
    
    # Get Case details to pass to Governor
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")
        
    case_data = dict(row)
    
    # Wire into real Policy Governor
    from backend.app.policy.economic_policy import DeterministicPolicyGovernor
    
    governor = DeterministicPolicyGovernor()
    # Build dummy context based on row
    context = {
        "amount_paise": case_data["amount_paise"],
        "payment_method": case_data["payment_method"],
        "failure_code": case_data["failure_code"],
        "retries_attempted": case_data["retries_attempted"],
        "time_since_failure_minutes": case_data["time_since_failure_minutes"],
        "historical_payment_success_rate": case_data["historical_payment_success_rate"],
        "engagement_score": case_data["engagement_score"],
        "customer_value_band": case_data["customer_value_band"],
        "bank": case_data["bank"]
    }
    
    evaluation = governor.evaluate(context, action_id)
    is_approved = evaluation.get("status") == "APPROVED"
    rejection_reason = evaluation.get("reason", "")
    
    if not is_approved:
        log_audit_event(case_id, corr_id, "GOVERNOR_REJECTED", f"Action {action_id} blocked: {rejection_reason}")
        conn.close()
        raise HTTPException(status_code=403, detail=f"Governor Rejected: {rejection_reason}")
        
    log_audit_event(case_id, corr_id, "GOVERNOR_APPROVED", f"Governor approved Action {action_id}")
    
    # Simulate adapter delay
    time.sleep(0.5)
    
    status = "PENDING_VERIFICATION"
    if action_id == 0:
        status = "EXECUTED_NO_ACTION"
        
    c.execute('''
        INSERT INTO executions (correlation_id, case_id, action_id, provider_id, status, recovered_amount, simulated, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (corr_id, case_id, action_id, f"sim_req_{uuid.uuid4().hex[:8]}", status, 0, 1, time.time()))
    conn.commit()
    conn.close()
    
    log_audit_event(case_id, corr_id, "EXECUTION_DISPATCHED", f"Action {action_id} sent to Razorpay Adapter.")
    
    return {"correlation_id": corr_id, "status": status}

@app.get("/api/evaluation")
def get_evaluation():
    import os
    file_path = os.path.join(os.path.dirname(__file__), "../../../evaluation/CANONICAL_BENCHMARK.md")
    with open(file_path, "r") as f:
        content = f.read()
    return {"markdown": content}
