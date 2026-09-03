from typing import Dict, Any, List
from pydantic import BaseModel, Field

class AgentRecommendation(BaseModel):
    diagnosis: str
    evidence: List[str]
    candidate_actions: List[int]
    recommended_action: int
    model_uplift: float
    expected_incremental_value_paise: int
    confidence: str
    policy_constraints: List[str]
    explanation: str

class AgentOrchestrator:
    def __init__(self, causal_policy, governor, adapter):
        self.causal_policy = causal_policy
        self.governor = governor
        self.adapter = adapter
        
    def generate_recommendation(self, context: Dict[str, Any], llm_explanation: str) -> AgentRecommendation:
        """
        The LLM provides the 'explanation' and 'diagnosis', but the numerical values MUST 
        come strictly from the causal policy. The LLM is NOT allowed to invent uplift.
        """
        decision = self.causal_policy.get_best_action(context)
        
        return AgentRecommendation(
            diagnosis="Analysis complete.",
            evidence=[],
            candidate_actions=[0,1,2,3,4,5],
            recommended_action=decision.get("recommended_action", 0),
            model_uplift=decision.get("estimated_uplift", 0.0),
            expected_incremental_value_paise=decision.get("expected_incremental_value_paise", 0),
            confidence=decision.get("confidence", "LOW"),
            policy_constraints=[],
            explanation=llm_explanation
        )
        
    def execute_recommendation(self, context: Dict[str, Any], recommendation: AgentRecommendation) -> Dict[str, Any]:
        """
        Takes an agent's recommendation and executes it via the governor and adapter.
        If an adversarial LLM tries to tamper with the recommendation obj, it fails here.
        """
        # 1. Re-verify the numerical reality (Don't trust the Agent object)
        true_decision = self.causal_policy.get_best_action(context)
        if recommendation.recommended_action != true_decision.get("recommended_action"):
            raise ValueError("Agent attempted to override Causal Policy recommendation.")
            
        # 2. Governor Check
        approval = self.governor.evaluate(context, recommendation.recommended_action)
        if approval["status"] != "APPROVED":
            raise ValueError(f"Agent recommendation rejected by Policy Governor: {approval.get('reason')}")
            
        # 3. Execution
        result = self.adapter.execute_action(
            action_id=approval["action_id"],
            context=context,
            governor_approval=approval
        )
        
        return result
