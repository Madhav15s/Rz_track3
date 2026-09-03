import os
import time
import uuid
import hashlib
import json
from typing import Dict, Any, Optional

try:
    import razorpay
except ImportError:
    razorpay = None

class UnauthorizedExecutionError(Exception):
    pass

class OutcomeLedger:
    def __init__(self):
        # Maps correlation_id to execution state
        self.executions: Dict[str, Dict[str, Any]] = {}
        # Maps provider_id to correlation_id
        self.provider_map: Dict[str, str] = {}
        # Set of processed webhook IDs to ensure idempotency
        self.processed_webhooks = set()

    def record_execution(self, correlation_id: str, case_id: str, action_id: int, provider_id: str, is_simulated: bool):
        self.executions[correlation_id] = {
            "case_id": case_id,
            "action_id": action_id,
            "provider_id": provider_id,
            "status": "PENDING_VERIFICATION",
            "recovered_amount": 0,
            "simulated": is_simulated,
            "timestamp": time.time()
        }
        if provider_id:
            self.provider_map[provider_id] = correlation_id

    def verify_webhook(self, webhook_id: str, provider_id: str, event_type: str, amount: int) -> Dict[str, Any]:
        if webhook_id in self.processed_webhooks:
            return {"status": "IGNORED", "reason": "DUPLICATE_WEBHOOK"}
            
        self.processed_webhooks.add(webhook_id)
        
        correlation_id = self.provider_map.get(provider_id)
        if not correlation_id:
            return {"status": "UNKNOWN", "reason": "PROVIDER_ID_NOT_FOUND"}
            
        execution = self.executions[correlation_id]
        
        if event_type in ['payment_link.paid', 'order.paid', 'payment.captured']:
            execution["status"] = "VERIFIED_RECOVERED"
            execution["recovered_amount"] = amount
            return {"status": "VERIFIED_RECOVERED", "correlation_id": correlation_id}
        elif event_type in ['payment.failed']:
            execution["status"] = "VERIFIED_FAILED"
            return {"status": "VERIFIED_FAILED", "correlation_id": correlation_id}
            
        return {"status": "UNKNOWN_EVENT", "correlation_id": correlation_id}

    def get_status(self, correlation_id: str):
        return self.executions.get(correlation_id, {"status": "UNKNOWN"})


class RazorpayTestAdapter:
    def __init__(self, ledger: OutcomeLedger):
        self.key_id = os.environ.get("RAZORPAY_KEY_ID")
        self.key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
        self.ledger = ledger
        
        # Idempotency cache for API calls
        self.idempotency_cache = {}
        
        self.client = None
        if self.key_id and self.key_secret and razorpay:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def _verify_governor_approval(self, governor_approval: Dict[str, Any], action_id: int, case_id: str):
        """
        Hard boundary: Ensure the LLM or any caller isn't forging requests.
        The caller MUST provide a valid governor_approval object explicitly approving THIS action for THIS case.
        """
        if not governor_approval or governor_approval.get('status') != 'APPROVED':
            raise UnauthorizedExecutionError("Execution rejected: Missing or invalid Governor approval.")
        
        if governor_approval.get('action_id') != action_id:
            raise UnauthorizedExecutionError(f"Execution rejected: Governor approved action {governor_approval.get('action_id')}, but {action_id} was requested.")
            
        if governor_approval.get('case_id') != case_id:
            raise UnauthorizedExecutionError("Execution rejected: Case ID mismatch in Governor approval.")

    def execute_action(self, action_id: int, context: Dict[str, Any], governor_approval: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the requested recovery action.
        """
        case_id = context.get('case_id')
        amount = context.get('amount_paise', 0)
        
        # 1. Enforce Boundary
        self._verify_governor_approval(governor_approval, action_id, case_id)
        
        # 2. Idempotency & Correlation
        idempotency_key = governor_approval.get('idempotency_key')
        if not idempotency_key:
            raise ValueError("idempotency_key missing from governor approval")
            
        correlation_id = governor_approval.get('correlation_id')
        if not correlation_id:
            raise ValueError("correlation_id missing from governor approval")
            
        if idempotency_key in self.idempotency_cache:
            return self.idempotency_cache[idempotency_key]
            
        # 3. Execution
        if action_id == 0:
            result = {
                "api_status": "SKIPPED",
                "provider_id": None,
                "correlation_id": correlation_id,
                "simulated": True
            }
        elif self.client:
            # Authentic Test-Mode Execution
            result = self._execute_real(action_id, case_id, amount, idempotency_key, correlation_id)
        else:
            # Simulated execution
            result = self._execute_simulated(action_id, case_id, amount, idempotency_key, correlation_id)
            
        self.idempotency_cache[idempotency_key] = result
        
        # 4. Record to ledger (API success != Revenue Recovered)
        if result.get("api_status") == "SUCCESS":
            self.ledger.record_execution(
                correlation_id=correlation_id,
                case_id=case_id,
                action_id=action_id,
                provider_id=result.get("provider_id"),
                is_simulated=result.get("simulated", True)
            )
            
        return result

    def _execute_real(self, action_id: int, case_id: str, amount: int, idempotency_key: str, correlation_id: str) -> Dict[str, Any]:
        try:
            if action_id in [1, 2]: # RETRY NOW / LATER -> Issue Payment Link
                pl_data = {
                    "amount": amount,
                    "currency": "INR",
                    "description": f"Recovery for {case_id}",
                    "reference_id": correlation_id,
                    "customer": {
                        "name": "Customer",
                        "contact": "+919999999999",
                        "email": "customer@example.com"
                    },
                    "notify": {"sms": True, "email": True},
                    "reminder_enable": True
                }
                payment_link = self.client.payment_link.create(pl_data)
                return {
                    "api_status": "SUCCESS",
                    "provider_id": payment_link.get('id'),
                    "correlation_id": correlation_id,
                    "simulated": False
                }
            elif action_id == 4: # ALTERNATE METHOD -> Issue new Order
                order_data = {
                    "amount": amount,
                    "currency": "INR",
                    "receipt": correlation_id
                }
                order = self.client.order.create(data=order_data)
                return {
                    "api_status": "SUCCESS",
                    "provider_id": order.get('id'),
                    "correlation_id": correlation_id,
                    "simulated": False
                }
            else:
                return {
                    "api_status": "SUCCESS",
                    "provider_id": f"sim_real_{uuid.uuid4().hex[:8]}",
                    "correlation_id": correlation_id,
                    "simulated": False
                }
        except Exception as e:
            # API failure doesn't mean payment failed, just system error
            return {
                "api_status": "ERROR",
                "error": str(e),
                "correlation_id": correlation_id,
                "simulated": False
            }

    def _execute_simulated(self, action_id: int, case_id: str, amount: int, idempotency_key: str, correlation_id: str) -> Dict[str, Any]:
        # Simulate network timeout occasionally if we wanted, but keep it deterministic for now
        sim_id = f"sim_req_{correlation_id}"
        return {
            "api_status": "SUCCESS",
            "provider_id": sim_id,
            "correlation_id": correlation_id,
            "simulated": True
        }
