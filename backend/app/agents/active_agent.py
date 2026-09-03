import json
from typing import Dict, Any

class ActiveAgentExplainer:
    """
    Active AI Agent Handler.
    This layer serves as a safe boundary for integrating an LLM.
    It passes strictly deterministic inputs to the LLM (if available) to generate 
    a 'diagnosis' and 'explanation', but it forces all quantitative, financial, 
    and policy fields to be populated directly by the deterministic Python models.
    """
    def __init__(self):
        pass
        
    def generate_explanation(self, 
                             context: Dict[str, Any], 
                             causal_effects: Dict[int, float], 
                             optimizer_decision: Dict[str, Any],
                             governor_approval: Dict[str, Any],
                             llm_mock_response: str = None) -> Dict[str, Any]:
        """
        Generates the final structured response.
        The LLM only controls 'diagnosis' and 'explanation'.
        Everything else is mapped directly from the verified math/policy engines.
        """
        selected_action = optimizer_decision['recommended_action']
        
        # In a real setup, we would prompt the LLM here using the context.
        # We simulate the LLM's prose generation:
        if not llm_mock_response:
            diagnosis = f"Payment failed due to {context.get('failure_code')}. Engagement is {context.get('engagement_score')}."
            explanation = f"Selected Action {selected_action} because it yields the highest expected incremental value while respecting safety boundaries."
        else:
            diagnosis = "LLM Diagnosis: " + llm_mock_response
            explanation = "LLM Explanation: " + llm_mock_response

        # STRICT STRUCTURAL OUTPUT
        # The agent CANNOT forge these numbers. They are hardcoded from the engines.
        structured_output = {
            "diagnosis": diagnosis,
            "evidence": {
                "failure_code": context.get('failure_code'),
                "amount": context.get('amount_paise'),
                "retries": context.get('retries_attempted')
            },
            "candidate_actions": [
                {
                    "action_id": a, 
                    "estimated_uplift": causal_effects[a]
                } for a in range(6)
            ],
            "selected_action": selected_action,
            "estimated_uplift": causal_effects[selected_action],
            "expected_incremental_value": optimizer_decision['expected_incremental_value'],
            "confidence": 0.95, # Would come from the model's conformal prediction interval
            "policy_constraints": {
                "status": governor_approval['status'],
                "reason": governor_approval.get('reason', '')
            },
            "explanation": explanation
        }
        
        return structured_output
