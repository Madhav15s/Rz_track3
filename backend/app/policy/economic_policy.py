from typing import Dict, Any, List, Optional
import time
import hashlib
from backend.app.causal.interfaces import TreatmentEffectModel

class ActionConfig:
    def __init__(self, action_id: int, name: str, cost: int, friction: int, risk: int):
        self.action_id = action_id
        self.name = name
        self.cost = cost
        self.friction = friction
        self.risk = risk

ACTION_CATALOG = {
    0: ActionConfig(0, "NO_ACTION", 0, 0, 0),
    1: ActionConfig(1, "RETRY_NOW", 100, 50, 20),
    2: ActionConfig(2, "RETRY_LATER", 100, 20, 10),
    3: ActionConfig(3, "PAYMENT_MESSAGE", 50, 100, 10),
    4: ActionConfig(4, "ALTERNATE_METHOD", 200, 150, 30),
    5: ActionConfig(5, "HUMAN_ESCALATION", 2500, 50, 10)
}

class EconomicPolicyOptimizer:
    def __init__(self, causal_model: TreatmentEffectModel, abstention_threshold: str = "LOW"):
        self.causal_model = causal_model
        self.abstention_threshold = abstention_threshold
        
    def get_best_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        amount = context.get('amount_paise', 0)
        effects = self.causal_model.predict_all_effects(context)
        
        best_action = 0
        best_value = 0.0
        details = []
        
        for a, uplift in effects.items():
            conf = self.causal_model.confidence(context, a)
            
            # Abstention: if confidence is LOW, we treat its uplift as 0 for optimization
            if conf == "LOW" and a != 0:
                uplift = 0.0
                
            cfg = ACTION_CATALOG.get(a)
            if not cfg: continue
            
            inc_value = (amount * uplift) - cfg.cost - cfg.friction - cfg.risk
            
            details.append({
                "action": a,
                "name": cfg.name,
                "uplift": uplift,
                "incremental_value": inc_value,
                "confidence": conf
            })
            
            if inc_value > best_value:
                best_value = inc_value
                best_action = a
                
        return {
            "recommended_action": best_action,
            "expected_incremental_value": best_value,
            "details": details
        }

class DeterministicPolicyGovernor:
    def __init__(self):
        pass
        
    def evaluate(self, context: Dict[str, Any], proposed_action: int) -> Dict[str, Any]:
        """
        Hard gatekeeper: evaluates if the proposed action is permitted.
        Returns the approval ticket which the execution adapter requires.
        """
        case_id = context.get('case_id', 'unknown')
        
        # 1. Hard Declines (e.g., Stolen Card, Account Closed) cannot be retried
        hard_decline_codes = ['CARD_STOLEN', 'ACCOUNT_CLOSED', 'FRAUD_SUSPECTED', 'BANK_DECLINE']
        if context.get('failure_code') in hard_decline_codes and proposed_action in [1, 2]:
            return {
                "status": "REJECTED",
                "reason": "Hard decline cannot be retried.",
                "case_id": case_id,
                "action_id": proposed_action
            }
            
        # Insufficient Funds should not be retried IMMEDIATELY
        if context.get('failure_code') == 'INSUFFICIENT_FUNDS' and proposed_action == 1:
            return {
                "status": "REJECTED",
                "reason": "Insufficient funds cannot be retried immediately.",
                "case_id": case_id,
                "action_id": proposed_action
            }
            
        # 2. Velocity / Retry Limits
        if context.get('retries_attempted', 0) >= 3 and proposed_action in [1, 2]:
            return {
                "status": "REJECTED",
                "reason": "Max retry velocity exceeded.",
                "case_id": case_id,
                "action_id": proposed_action
            }
            
        # Amount Limit
        if context.get('amount_paise', 0) > 5000000 and proposed_action in [1, 2, 4]:
            return {
                "status": "REJECTED",
                "reason": "Amount exceeds maximum permitted automated recovery limit.",
                "case_id": case_id,
                "action_id": proposed_action
            }
            
        # 3. High Risk / Low Engagement
        if context.get('engagement_score', 1.0) < 0.2 and proposed_action == 5:
            return {
                "status": "REJECTED",
                "reason": "Human escalation requires minimum engagement threshold.",
                "case_id": case_id,
                "action_id": proposed_action
            }
            
        correlation_id = f"corr_{case_id}_{int(time.time()*1000)}"
        idempotency_key = hashlib.sha256(f"{case_id}_{proposed_action}_{correlation_id}".encode()).hexdigest()
            
        return {
            "status": "APPROVED",
            "reason": "Passed all safety checks.",
            "case_id": case_id,
            "action_id": proposed_action,
            "correlation_id": correlation_id,
            "idempotency_key": idempotency_key
        }
