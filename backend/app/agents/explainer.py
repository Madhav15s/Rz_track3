from typing import Dict, Any, List

class AgentExplainer:
    def __init__(self):
        # In a real setup, this would be an API call to a reasoning LLM
        pass
        
    def generate_explanation(self, context: Dict[str, Any], decision: Dict[str, Any], policy_status: Dict[str, Any]) -> str:
        """
        Synthesizes the incident context, causal model's recommendation, 
        and the governor's policy into a human-readable explanation.
        """
        action_names = {
            0: "NO ACTION",
            1: "RETRY NOW",
            2: "RETRY LATER",
            3: "PAYMENT MESSAGE",
            4: "ALTERNATE METHOD",
            5: "HUMAN ESCALATION"
        }
        
        failure = context.get('failure_code', 'UNKNOWN')
        rec_action = decision.get('recommended_action', 0)
        action_name = action_names.get(rec_action, "UNKNOWN")
        expected_value = decision.get('expected_incremental_value', 0) / 100.0 # to INR
        
        candidates = decision.get('details', [])
        best_candidate = next((c for c in candidates if c['action'] == rec_action), None)
        uplift = best_candidate['uplift'] * 100 if best_candidate else 0.0
        confidence = best_candidate['confidence'] if best_candidate else "LOW"
        
        # Machine Explanation
        machine_expl = (
            f"MACHINE:\n"
            f"action = {action_name}\n"
            f"uplift = {uplift:.2f}%\n"
            f"expected_incremental_value = {expected_value:.2f} INR\n"
            f"confidence = {confidence}\n"
        )
        
        # Human Explanation (simulated LLM generation)
        human_expl = "HUMAN:\n"
        
        if policy_status['status'] == 'REJECTED':
            human_expl += (
                f"The causal model recommended {action_name} due to an estimated uplift of {uplift:.2f}%, "
                f"but the deterministic policy governor REJECTED this action because: {policy_status['reason']}. "
                f"Therefore, the system abstained from automated recovery."
            )
        elif rec_action == 0:
            human_expl += (
                f"No intervention demonstrated a positive net economic value for this {failure}. "
                f"The system abstained to prevent unnecessary friction and cost."
            )
        else:
            human_expl += (
                f"For this {failure}, {action_name} offers a strong causal uplift of {uplift:.2f}%. "
                f"After accounting for friction and operational costs, the expected net incremental value is {expected_value:.2f} INR. "
                f"The policy governor APPROVED this action."
            )
            
        return machine_expl + "\n" + human_expl

