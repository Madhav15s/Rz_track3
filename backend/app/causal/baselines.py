import pandas as pd
from typing import Dict, Any, List
from backend.app.causal.interfaces import TreatmentEffectModel

class DoNothingBaseline(TreatmentEffectModel):
    def fit(self, df_features: pd.DataFrame, df_treatments: pd.DataFrame, df_outcomes: pd.DataFrame):
        pass
        
    def predict_effect(self, context: Dict[str, Any], action: int) -> float:
        return 0.0
        
    def predict_all_effects(self, context: Dict[str, Any]) -> Dict[int, float]:
        return {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
        
    def confidence(self, context: Dict[str, Any], action: int) -> str:
        return "HIGH"
        
    def supported_actions(self) -> List[int]:
        return [0, 1, 2, 3, 4, 5]
        
    def model_version(self) -> str:
        return "baseline-do-nothing"

class FixedDunningBaseline(TreatmentEffectModel):
    def fit(self, df_features: pd.DataFrame, df_treatments: pd.DataFrame, df_outcomes: pd.DataFrame):
        pass
        
    def predict_effect(self, context: Dict[str, Any], action: int) -> float:
        # Hardcoded logic simulating a generic rules engine
        if action == 1 and context.get("failure_code") != "INSUFFICIENT_FUNDS":
            return 0.1
        if action == 2 and context.get("failure_code") == "INSUFFICIENT_FUNDS":
            return 0.1
        return 0.0
        
    def predict_all_effects(self, context: Dict[str, Any]) -> Dict[int, float]:
        effects = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
        if context.get("failure_code") != "INSUFFICIENT_FUNDS": effects[1] = 0.1
        if context.get("failure_code") == "INSUFFICIENT_FUNDS": effects[2] = 0.1
        return effects
        
    def confidence(self, context: Dict[str, Any], action: int) -> str:
        return "HIGH"
        
    def supported_actions(self) -> List[int]:
        return [0, 1, 2, 3, 4, 5]
        
    def model_version(self) -> str:
        return "baseline-fixed-dunning"
